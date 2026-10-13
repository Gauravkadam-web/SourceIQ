"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-13 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector
from app.core.config import settings

# revision identifiers, used by Alembic.
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Enable pgvector extension (if available in PostgreSQL install)
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
    # Try enabling vector extension; if not yet installed in PG server directory, log gracefully
    op.execute("""
        DO $$
        BEGIN
            CREATE EXTENSION IF NOT EXISTS vector;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'pgvector extension not yet found in PostgreSQL sharedir; install extension files before embedding vectors.';
        END
        $$;
    """)

    # 2. Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('idx_workspaces_created_at', 'workspaces', ['created_at'], unique=False)

    # 3. Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), server_default='application/pdf', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('page_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('chunk_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("status IN ('PENDING', 'PARSING', 'EMBEDDING', 'READY', 'FAILED')", name='chk_document_status'),
    )
    op.create_index('idx_documents_workspace_id', 'documents', ['workspace_id'], unique=False)
    op.create_index('idx_documents_status', 'documents', ['status'], unique=False)

    # 4. Create document_chunks table
    # Vector column uses configured dimension (768 for Gemini)
    op.create_table(
        'document_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(settings.EMBEDDING_DIMENSIONS), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('document_id', 'chunk_index', name='uq_doc_chunk_index'),
    )
    op.create_index('idx_chunks_workspace_id', 'document_chunks', ['workspace_id'], unique=False)
    op.create_index('idx_chunks_document_id', 'document_chunks', ['document_id'], unique=False)
    op.create_index('idx_chunks_page_number', 'document_chunks', ['document_id', 'page_number'], unique=False)

    # Vector index using HNSW with cosine distance (<=>)
    op.execute("""
        DO $$
        BEGIN
            CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'HNSW index creation deferred until vector extension is active.';
        END
        $$;
    """)

    # 5. Create query_runs table
    op.create_table(
        'query_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='COMPLETED', nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("status IN ('GROUNDED', 'INSUFFICIENT_EVIDENCE', 'CITATION_FAILED', 'ERROR', 'COMPLETED')", name='chk_query_status'),
    )
    op.create_index('idx_query_runs_workspace_id', 'query_runs', ['workspace_id'], unique=False)
    op.create_index('idx_query_runs_created_at', 'query_runs', ['created_at'], unique=False)

    # 6. Create citation_logs table
    op.create_table(
        'citation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('query_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('query_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('document_chunks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('claim_snippet', sa.Text(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('is_valid', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('idx_citation_logs_query_run', 'citation_logs', ['query_run_id'], unique=False)
    op.create_index('idx_citation_logs_chunk', 'citation_logs', ['chunk_id'], unique=False)


def downgrade() -> None:
    op.drop_table('citation_logs')
    op.drop_table('query_runs')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('workspaces')
