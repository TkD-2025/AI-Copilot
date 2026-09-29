"""SQLAlchemy ORM models for the AI Copilot persistence layer."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.database.database import Base


user_role = postgresql.ENUM("admin", "operator", "viewer", name="user_role", create_type=False)
session_status = postgresql.ENUM(
    "active", "completed", "terminated", name="session_status", create_type=False
)
plan_state = postgresql.ENUM(
    "pending",
    "waiting_approval",
    "ready",
    "completed",
    "failed",
    "skipped",
    name="plan_state",
    create_type=False,
)
execution_status = postgresql.ENUM(
    "running",
    "succeeded",
    "failed",
    "cancelled",
    "timed_out",
    name="execution_status",
    create_type=False,
)
risk_level = postgresql.ENUM(
    "low", "medium", "high", "critical", name="risk_level", create_type=False
)
approval_decision = postgresql.ENUM(
    "approved", "rejected", "modified", name="approval_decision", create_type=False
)


class User(Base):
    """Application user record for authentication and authorization context."""

    __tablename__ = "users"
    __table_args__ = (Index("ix_users_created_at", "created_at"),)

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(user_role, nullable=False)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship("Permission", back_populates="user", cascade="all, delete-orphan")
    approvals = relationship(
        "NodeApproval",
        back_populates="decider",
        foreign_keys="NodeApproval.decided_by",
        cascade="all, delete-orphan",
    )


class Session(Base):
    """Execution session that groups an intent, planning, and runtime activity."""

    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_user_id", "user_id"),
        Index("ix_sessions_status", "status"),
        Index("ix_sessions_started_at", "started_at"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mode = Column(String(50), nullable=False)
    started_at = Column(DateTime(timezone=False), nullable=False)
    ended_at = Column(DateTime(timezone=False), nullable=True)
    status = Column(session_status, nullable=False)

    user = relationship("User", back_populates="sessions")
    intents = relationship("Intent", back_populates="session", cascade="all, delete-orphan")


class Intent(Base):
    """Parsed user intent captured from a session input."""

    __tablename__ = "intents"
    __table_args__ = (
        Index("ix_intents_session_id", "session_id"),
        Index("ix_intents_created_at", "created_at"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    raw_input = Column(Text, nullable=False)
    parsed_intent = Column(postgresql.JSONB(astext_type=Text), nullable=False)
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    session = relationship("Session", back_populates="intents")
    plans = relationship("Plan", back_populates="intent", cascade="all, delete-orphan")


class Plan(Base):
    """Historical plan snapshot derived from an intent."""

    __tablename__ = "plans"
    __table_args__ = (
        Index("ix_plans_intent_id", "intent_id"),
        Index("ix_plans_status", "status"),
        Index("ix_plans_created_at", "created_at"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intent_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("intents.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String(50), nullable=False)
    graph_snapshot = Column(postgresql.JSONB(astext_type=Text), nullable=True)
    planner_name = Column(String(255), nullable=False)
    planner_version = Column(String(100), nullable=False)
    planner_latency_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    intent = relationship("Intent", back_populates="plans")
    nodes = relationship("PlanNode", back_populates="plan", cascade="all, delete-orphan")


class PlanNode(Base):
    """Single plan node that acts as the hub for executions and approval records."""

    __tablename__ = "plan_nodes"
    __table_args__ = (
        Index("ix_plan_nodes_plan_id", "plan_id"),
        Index("ix_plan_nodes_state", "state"),
        Index("ix_plan_nodes_created_at", "created_at"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    action_type = Column(String(50), nullable=False)
    action_payload = Column(postgresql.JSONB(astext_type=Text), nullable=True)
    risk_level = Column(risk_level, nullable=False)
    state = Column(plan_state, nullable=False)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    plan = relationship("Plan", back_populates="nodes")
    executions = relationship("Execution", back_populates="plan_node", cascade="all, delete-orphan")
    approvals = relationship("NodeApproval", back_populates="plan_node", cascade="all, delete-orphan")


class Environment(Base):
    """Execution environment available to run an action."""

    __tablename__ = "environments"
    __table_args__ = (
        Index("ix_environments_status", "status"),
        Index("ix_environments_created_at", "created_at"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    connection_config = Column(postgresql.JSONB(astext_type=Text), nullable=True)
    is_sandboxed = Column(Boolean, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    executions = relationship("Execution", back_populates="environment")


class Execution(Base):
    """Runtime execution record for a plan node, allowing retries."""

    __tablename__ = "executions"
    __table_args__ = (
        Index("ix_executions_plan_node_id", "plan_node_id"),
        Index("ix_executions_environment_id", "environment_id"),
        Index("ix_executions_status", "status"),
        Index("ix_executions_created_at", "created_at"),
        Index("ix_executions_plan_node_id_attempt_number_desc", "plan_node_id", text("attempt_number DESC")),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_node_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("plan_nodes.id", ondelete="CASCADE"),
        nullable=False,
    )
    environment_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("environments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    attempt_number = Column(Integer, nullable=False, server_default="1")
    started_at = Column(DateTime(timezone=False), nullable=False)
    finished_at = Column(DateTime(timezone=False), nullable=True)
    status = Column(execution_status, nullable=False)
    risk_score = Column(Float, nullable=True)
    output = Column(postgresql.JSONB(astext_type=Text), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    plan_node = relationship("PlanNode", back_populates="executions")
    environment = relationship("Environment", back_populates="executions")
    observations = relationship(
        "ExecutionObservation", back_populates="execution", cascade="all, delete-orphan"
    )


class ExecutionObservation(Base):
    """Structured observations emitted during execution."""

    __tablename__ = "execution_observations"
    __table_args__ = (
        Index("ix_execution_observations_execution_id", "execution_id"),
        Index("ix_execution_observations_created_at", "created_at"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
    )
    observation_type = Column(String(50), nullable=False)
    data = Column(postgresql.JSONB(astext_type=Text), nullable=False)
    validated = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    execution = relationship("Execution", back_populates="observations")


class Permission(Base):
    """Permission grant or denial for a specific action type and scope."""

    __tablename__ = "permissions"
    __table_args__ = (
        Index("ix_permissions_user_id", "user_id"),
        Index("ix_permissions_action_type", "action_type"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    action_type = Column(String(100), nullable=False)
    allowed = Column(Boolean, nullable=False)
    scope = Column(postgresql.JSONB(astext_type=Text), nullable=True)

    user = relationship("User", back_populates="permissions")


class SafetyRule(Base):
    """Safety rule used for validation and approval control."""

    __tablename__ = "safety_rules"
    __table_args__ = (
        Index("ix_safety_rules_rule_type", "rule_type"),
        Index("ix_safety_rules_active", "active"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(255), nullable=False)
    pattern = Column(postgresql.JSONB(astext_type=Text), nullable=False)
    rule_type = Column(String(50), nullable=False)
    risk_weight = Column(Float, nullable=False)
    active = Column(Boolean, nullable=False)


class NodeApproval(Base):
    """Approval decision attached to a node in a plan."""

    __tablename__ = "node_approvals"
    __table_args__ = (
        Index("ix_node_approvals_plan_node_id", "plan_node_id"),
        Index("ix_node_approvals_decision", "decision"),
        Index("ix_node_approvals_decided_at", "decided_at"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_node_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("plan_nodes.id", ondelete="CASCADE"),
        nullable=False,
    )
    requested_by = Column(String(255), nullable=False)
    decided_by = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    decision = Column(approval_decision, nullable=False)
    comment = Column(String(1000), nullable=True)
    decided_at = Column(DateTime(timezone=False), nullable=True)

    plan_node = relationship("PlanNode", back_populates="approvals")
    decider = relationship("User", back_populates="approvals", foreign_keys=[decided_by])


class AuditLog(Base):
    """Polymorphic audit trail for plan, node, execution, and approval events."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_related_entity_type_related_entity_id", "related_entity_type", "related_entity_id"),
        Index("ix_audit_logs_timestamp", "timestamp"),
    )

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor = Column(String(255), nullable=False)
    action_summary = Column(String(500), nullable=False)
    related_entity_type = Column(String(50), nullable=False)
    related_entity_id = Column(postgresql.UUID(as_uuid=True), nullable=False)
    reasoning = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
