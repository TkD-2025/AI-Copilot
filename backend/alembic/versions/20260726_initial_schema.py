

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "20260726_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'operator', 'viewer')")
    op.execute("CREATE TYPE session_status AS ENUM ('active', 'completed', 'terminated')")
    op.execute("CREATE TYPE plan_state AS ENUM ('pending', 'waiting_approval', 'ready', 'completed', 'failed', 'skipped')")
    op.execute("CREATE TYPE execution_status AS ENUM ('running', 'succeeded', 'failed', 'cancelled', 'timed_out')")
    op.execute("CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical')")
    op.execute("CREATE TYPE approval_decision AS ENUM ('approved', 'rejected', 'modified')")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", postgresql.ENUM(name="user_role", create_type=False), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_created_at"), "users", ["created_at"], unique=False)

    op.create_table(
        "environments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("connection_config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_sandboxed", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_environments_status"), "environments", ["status"], unique=False)
    op.create_index(op.f("ix_environments_created_at"), "environments", ["created_at"], unique=False)

    op.create_table(
        "safety_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_name", sa.String(length=255), nullable=False),
        sa.Column("pattern", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rule_type", sa.String(length=50), nullable=False),
        sa.Column("risk_weight", sa.Float(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_safety_rules_rule_type"), "safety_rules", ["rule_type"], unique=False)
    op.create_index(op.f("ix_safety_rules_active"), "safety_rules", ["active"], unique=False)

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mode", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("status", postgresql.ENUM(name="session_status", create_type=False), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_sessions_status"), "sessions", ["status"], unique=False)
    op.create_index(op.f("ix_sessions_started_at"), "sessions", ["started_at"], unique=False)

    op.create_table(
        "intents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("raw_input", sa.Text(), nullable=False),
        sa.Column("parsed_intent", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_intents_session_id"), "intents", ["session_id"], unique=False)
    op.create_index(op.f("ix_intents_created_at"), "intents", ["created_at"], unique=False)

    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("intent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("graph_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("planner_name", sa.String(length=255), nullable=False),
        sa.Column("planner_version", sa.String(length=100), nullable=False),
        sa.Column("planner_latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["intent_id"], ["intents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plans_intent_id"), "plans", ["intent_id"], unique=False)
    op.create_index(op.f("ix_plans_status"), "plans", ["status"], unique=False)
    op.create_index(op.f("ix_plans_created_at"), "plans", ["created_at"], unique=False)

    op.create_table(
        "plan_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("action_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("risk_level", postgresql.ENUM(name="risk_level", create_type=False), nullable=False),
        sa.Column("state", postgresql.ENUM(name="plan_state", create_type=False), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plan_nodes_plan_id"), "plan_nodes", ["plan_id"], unique=False)
    op.create_index(op.f("ix_plan_nodes_state"), "plan_nodes", ["state"], unique=False)
    op.create_index(op.f("ix_plan_nodes_created_at"), "plan_nodes", ["created_at"], unique=False)

    op.create_table(
        "executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_node_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attempt_number", sa.Integer(), server_default="1", nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("status", postgresql.ENUM(name="execution_status", create_type=False), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["plan_node_id"], ["plan_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_executions_plan_node_id"), "executions", ["plan_node_id"], unique=False)
    op.create_index(op.f("ix_executions_environment_id"), "executions", ["environment_id"], unique=False)
    op.create_index(op.f("ix_executions_status"), "executions", ["status"], unique=False)
    op.create_index(op.f("ix_executions_created_at"), "executions", ["created_at"], unique=False)
    op.create_index(
        op.f("ix_executions_plan_node_id_attempt_number_desc"),
        "executions",
        ["plan_node_id", sa.text("attempt_number DESC")],
        unique=False,
    )

    op.create_table(
        "execution_observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_type", sa.String(length=50), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("validated", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["execution_id"], ["executions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_execution_observations_execution_id"), "execution_observations", ["execution_id"], unique=False)
    op.create_index(op.f("ix_execution_observations_created_at"), "execution_observations", ["created_at"], unique=False)

    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_type", sa.String(length=100), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False),
        sa.Column("scope", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permissions_user_id"), "permissions", ["user_id"], unique=False)
    op.create_index(op.f("ix_permissions_action_type"), "permissions", ["action_type"], unique=False)

    op.create_table(
        "node_approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_node_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by", sa.String(length=255), nullable=False),
        sa.Column("decided_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decision", postgresql.ENUM(name="approval_decision", create_type=False), nullable=False),
        sa.Column("comment", sa.String(length=1000), nullable=True),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["plan_node_id"], ["plan_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["decided_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_node_approvals_plan_node_id"), "node_approvals", ["plan_node_id"], unique=False)
    op.create_index(op.f("ix_node_approvals_decision"), "node_approvals", ["decision"], unique=False)
    op.create_index(op.f("ix_node_approvals_decided_at"), "node_approvals", ["decided_at"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("action_summary", sa.String(length=500), nullable=False),
        sa.Column("related_entity_type", sa.String(length=50), nullable=False),
        sa.Column("related_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_logs_related_entity_type_related_entity_id"),
        "audit_logs",
        ["related_entity_type", "related_entity_id"],
        unique=False,
    )
    op.create_index(op.f("ix_audit_logs_timestamp"), "audit_logs", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_timestamp"), table_name="audit_logs")
    op.drop_index(
        op.f("ix_audit_logs_related_entity_type_related_entity_id"),
        table_name="audit_logs",
    )
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_node_approvals_decided_at"), table_name="node_approvals")
    op.drop_index(op.f("ix_node_approvals_decision"), table_name="node_approvals")
    op.drop_index(op.f("ix_node_approvals_plan_node_id"), table_name="node_approvals")
    op.drop_table("node_approvals")

    op.drop_index(op.f("ix_permissions_action_type"), table_name="permissions")
    op.drop_index(op.f("ix_permissions_user_id"), table_name="permissions")
    op.drop_table("permissions")

    op.drop_index(op.f("ix_execution_observations_created_at"), table_name="execution_observations")
    op.drop_index(op.f("ix_execution_observations_execution_id"), table_name="execution_observations")
    op.drop_table("execution_observations")

    op.drop_index(op.f("ix_executions_plan_node_id_attempt_number_desc"), table_name="executions")
    op.drop_index(op.f("ix_executions_created_at"), table_name="executions")
    op.drop_index(op.f("ix_executions_status"), table_name="executions")
    op.drop_index(op.f("ix_executions_environment_id"), table_name="executions")
    op.drop_index(op.f("ix_executions_plan_node_id"), table_name="executions")
    op.drop_table("executions")

    op.drop_index(op.f("ix_plan_nodes_created_at"), table_name="plan_nodes")
    op.drop_index(op.f("ix_plan_nodes_state"), table_name="plan_nodes")
    op.drop_index(op.f("ix_plan_nodes_plan_id"), table_name="plan_nodes")
    op.drop_table("plan_nodes")

    op.drop_index(op.f("ix_plans_created_at"), table_name="plans")
    op.drop_index(op.f("ix_plans_status"), table_name="plans")
    op.drop_index(op.f("ix_plans_intent_id"), table_name="plans")
    op.drop_table("plans")

    op.drop_index(op.f("ix_intents_created_at"), table_name="intents")
    op.drop_index(op.f("ix_intents_session_id"), table_name="intents")
    op.drop_table("intents")

    op.drop_index(op.f("ix_sessions_started_at"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_status"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_table("sessions")

    op.drop_index(op.f("ix_safety_rules_active"), table_name="safety_rules")
    op.drop_index(op.f("ix_safety_rules_rule_type"), table_name="safety_rules")
    op.drop_table("safety_rules")

    op.drop_index(op.f("ix_environments_created_at"), table_name="environments")
    op.drop_index(op.f("ix_environments_status"), table_name="environments")
    op.drop_table("environments")

    op.drop_index(op.f("ix_users_created_at"), table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS approval_decision")
    op.execute("DROP TYPE IF EXISTS risk_level")
    op.execute("DROP TYPE IF EXISTS execution_status")
    op.execute("DROP TYPE IF EXISTS plan_state")
    op.execute("DROP TYPE IF EXISTS session_status")
    op.execute("DROP TYPE IF EXISTS user_role")
