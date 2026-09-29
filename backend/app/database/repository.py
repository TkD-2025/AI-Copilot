"""Basic repository helpers for the persistence models."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.database.models import (
    AuditLog,
    Environment,
    Execution,
    ExecutionObservation,
    Intent,
    NodeApproval,
    Permission,
    Plan,
    PlanNode,
    SafetyRule,
    Session,
    User,
    approval_decision,
    execution_status,
    plan_state,
    session_status,
)


# User repository helpers

def create_user(db: Session, *, name: str, email: str, role: str) -> User:
    user = User(name=name, email=email, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update_user_role(db: Session, user: User, role: str) -> User:
    user.role = role
    db.commit()
    db.refresh(user)
    return user


# Session repository helpers

def create_session(
    db: Session,
    *,
    user_id: str,
    mode: str,
    started_at: Any,
    status: str,
    ended_at: Any | None = None,
) -> Session:
    session = Session(user_id=user_id, mode=mode, started_at=started_at, ended_at=ended_at, status=status)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_id(db: Session, session_id: str) -> Session | None:
    return db.query(Session).filter(Session.id == session_id).first()


def list_sessions(db: Session, skip: int = 0, limit: int = 100) -> list[Session]:
    return db.query(Session).offset(skip).limit(limit).all()


def update_session_status(db: Session, session: Session, status: str) -> Session:
    session.status = status
    db.commit()
    db.refresh(session)
    return session


# Intent repository helpers

def create_intent(
    db: Session,
    *,
    session_id: str,
    raw_input: str,
    parsed_intent: dict[str, Any],
    confidence_score: float,
) -> Intent:
    intent = Intent(
        session_id=session_id,
        raw_input=raw_input,
        parsed_intent=parsed_intent,
        confidence_score=confidence_score,
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)
    return intent


def get_intent_by_id(db: Session, intent_id: str) -> Intent | None:
    return db.query(Intent).filter(Intent.id == intent_id).first()


def list_intents(db: Session, skip: int = 0, limit: int = 100) -> list[Intent]:
    return db.query(Intent).offset(skip).limit(limit).all()


# Plan repository helpers

def create_plan(
    db: Session,
    *,
    intent_id: str,
    status: str,
    graph_snapshot: dict[str, Any] | None,
    planner_name: str,
    planner_version: str,
    planner_latency_ms: int,
) -> Plan:
    plan = Plan(
        intent_id=intent_id,
        status=status,
        graph_snapshot=graph_snapshot,
        planner_name=planner_name,
        planner_version=planner_version,
        planner_latency_ms=planner_latency_ms,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_plan_by_id(db: Session, plan_id: str) -> Plan | None:
    return db.query(Plan).filter(Plan.id == plan_id).first()


def list_plans(db: Session, skip: int = 0, limit: int = 100) -> list[Plan]:
    return db.query(Plan).offset(skip).limit(limit).all()


def update_plan_status(db: Session, plan: Plan, status: str) -> Plan:
    plan.status = status
    db.commit()
    db.refresh(plan)
    return plan


# Plan node repository helpers

def create_plan_node(
    db: Session,
    *,
    plan_id: str,
    action_type: str,
    action_payload: dict[str, Any] | None,
    risk_level: str,
    state: str,
) -> PlanNode:
    node = PlanNode(
        plan_id=plan_id,
        action_type=action_type,
        action_payload=action_payload,
        risk_level=risk_level,
        state=state,
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def get_plan_node_by_id(db: Session, plan_node_id: str) -> PlanNode | None:
    return db.query(PlanNode).filter(PlanNode.id == plan_node_id).first()


def list_plan_nodes(db: Session, skip: int = 0, limit: int = 100) -> list[PlanNode]:
    return db.query(PlanNode).offset(skip).limit(limit).all()


def update_plan_node_state(db: Session, plan_node: PlanNode, state: str) -> PlanNode:
    plan_node.state = state
    db.commit()
    db.refresh(plan_node)
    return plan_node


# Environment repository helpers

def create_environment(
    db: Session,
    *,
    name: str,
    type: str,
    connection_config: dict[str, Any] | None,
    is_sandboxed: bool,
    status: str,
) -> Environment:
    environment = Environment(
        name=name,
        type=type,
        connection_config=connection_config,
        is_sandboxed=is_sandboxed,
        status=status,
    )
    db.add(environment)
    db.commit()
    db.refresh(environment)
    return environment


def get_environment_by_id(db: Session, environment_id: str) -> Environment | None:
    return db.query(Environment).filter(Environment.id == environment_id).first()


def list_environments(db: Session, skip: int = 0, limit: int = 100) -> list[Environment]:
    return db.query(Environment).offset(skip).limit(limit).all()


def update_environment_status(db: Session, environment: Environment, status: str) -> Environment:
    environment.status = status
    db.commit()
    db.refresh(environment)
    return environment


# Execution repository helpers

def create_execution(
    db: Session,
    *,
    plan_node_id: str,
    environment_id: str,
    attempt_number: int,
    started_at: Any,
    finished_at: Any | None,
    status: str,
    risk_score: float | None,
    output: dict[str, Any] | None,
    error_message: str | None,
) -> Execution:
    execution = Execution(
        plan_node_id=plan_node_id,
        environment_id=environment_id,
        attempt_number=attempt_number,
        started_at=started_at,
        finished_at=finished_at,
        status=status,
        risk_score=risk_score,
        output=output,
        error_message=error_message,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


def get_execution_by_id(db: Session, execution_id: str) -> Execution | None:
    return db.query(Execution).filter(Execution.id == execution_id).first()


def list_executions(db: Session, skip: int = 0, limit: int = 100) -> list[Execution]:
    return db.query(Execution).offset(skip).limit(limit).all()


def get_latest_execution_for_node(db: Session, plan_node_id: str) -> Execution | None:
    return (
        db.query(Execution)
        .filter(Execution.plan_node_id == plan_node_id)
        .order_by(Execution.attempt_number.desc())
        .first()
    )


def update_execution_status(db: Session, execution: Execution, status: str) -> Execution:
    execution.status = status
    db.commit()
    db.refresh(execution)
    return execution


# Execution observation repository helpers

def create_execution_observation(
    db: Session,
    *,
    execution_id: str,
    observation_type: str,
    data: dict[str, Any],
    validated: bool,
) -> ExecutionObservation:
    observation = ExecutionObservation(
        execution_id=execution_id,
        observation_type=observation_type,
        data=data,
        validated=validated,
    )
    db.add(observation)
    db.commit()
    db.refresh(observation)
    return observation


def get_execution_observation_by_id(db: Session, observation_id: str) -> ExecutionObservation | None:
    return db.query(ExecutionObservation).filter(ExecutionObservation.id == observation_id).first()


def list_execution_observations(db: Session, skip: int = 0, limit: int = 100) -> list[ExecutionObservation]:
    return db.query(ExecutionObservation).offset(skip).limit(limit).all()


# Permission repository helpers

def create_permission(
    db: Session,
    *,
    user_id: str | None,
    action_type: str,
    allowed: bool,
    scope: dict[str, Any] | None,
) -> Permission:
    permission = Permission(user_id=user_id, action_type=action_type, allowed=allowed, scope=scope)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def get_permission_by_id(db: Session, permission_id: str) -> Permission | None:
    return db.query(Permission).filter(Permission.id == permission_id).first()


def list_permissions(db: Session, skip: int = 0, limit: int = 100) -> list[Permission]:
    return db.query(Permission).offset(skip).limit(limit).all()


def update_permission_allowed(db: Session, permission: Permission, allowed: bool) -> Permission:
    permission.allowed = allowed
    db.commit()
    db.refresh(permission)
    return permission


# Safety rule repository helpers

def create_safety_rule(
    db: Session,
    *,
    rule_name: str,
    pattern: dict[str, Any],
    rule_type: str,
    risk_weight: float,
    active: bool,
) -> SafetyRule:
    rule = SafetyRule(
        rule_name=rule_name,
        pattern=pattern,
        rule_type=rule_type,
        risk_weight=risk_weight,
        active=active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_safety_rule_by_id(db: Session, safety_rule_id: str) -> SafetyRule | None:
    return db.query(SafetyRule).filter(SafetyRule.id == safety_rule_id).first()


def list_safety_rules(db: Session, skip: int = 0, limit: int = 100) -> list[SafetyRule]:
    return db.query(SafetyRule).offset(skip).limit(limit).all()


def update_safety_rule_active(db: Session, rule: SafetyRule, active: bool) -> SafetyRule:
    rule.active = active
    db.commit()
    db.refresh(rule)
    return rule


# Node approval repository helpers

def create_node_approval(
    db: Session,
    *,
    plan_node_id: str,
    requested_by: str,
    decided_by: str | None,
    decision: str,
    comment: str | None,
    decided_at: Any | None,
) -> NodeApproval:
    approval = NodeApproval(
        plan_node_id=plan_node_id,
        requested_by=requested_by,
        decided_by=decided_by,
        decision=decision,
        comment=comment,
        decided_at=decided_at,
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def get_node_approval_by_id(db: Session, approval_id: str) -> NodeApproval | None:
    return db.query(NodeApproval).filter(NodeApproval.id == approval_id).first()


def list_node_approvals(db: Session, skip: int = 0, limit: int = 100) -> list[NodeApproval]:
    return db.query(NodeApproval).offset(skip).limit(limit).all()


def update_node_approval_decision(
    db: Session,
    approval: NodeApproval,
    decision: str,
) -> NodeApproval:
    approval.decision = decision
    db.commit()
    db.refresh(approval)
    return approval


# Audit log repository helpers

def create_audit_log(
    db: Session,
    *,
    actor: str,
    action_summary: str,
    related_entity_type: str,
    related_entity_id: str,
    reasoning: str | None,
) -> AuditLog:
    log = AuditLog(
        actor=actor,
        action_summary=action_summary,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        reasoning=reasoning,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_audit_log_by_id(db: Session, audit_log_id: str) -> AuditLog | None:
    return db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()


def list_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> list[AuditLog]:
    return db.query(AuditLog).offset(skip).limit(limit).all()
