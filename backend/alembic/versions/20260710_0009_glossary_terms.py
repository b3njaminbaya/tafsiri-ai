"""glossary_terms table (admin-managed, replaces ml-service's hardcoded dict)

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "glossary_terms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("source_lang", sa.String(length=16), nullable=False),
        sa.Column("target_lang", sa.String(length=16), nullable=False),
        sa.Column("source_term", sa.String(length=255), nullable=False),
        sa.Column("target_term", sa.String(length=255), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_glossary_terms_id", "glossary_terms", ["id"])
    op.create_index("ix_glossary_terms_domain", "glossary_terms", ["domain"])

    # Seed with the same terms ml-service previously hardcoded (Phase 2), so
    # existing domain-translation behavior doesn't regress on upgrade.
    seed = [
        ("medical", "en", "es", "prescription", "receta médica"),
        ("medical", "en", "es", "diagnosis", "diagnóstico"),
        ("medical", "en", "es", "dosage", "dosis"),
        ("medical", "en", "fr", "prescription", "ordonnance"),
        ("medical", "en", "fr", "diagnosis", "diagnostic"),
        ("medical", "en", "fr", "dosage", "posologie"),
        ("medical", "en", "sw", "prescription", "dawa iliyoagizwa"),
        ("medical", "en", "sw", "diagnosis", "utambuzi"),
        ("medical", "en", "sw", "dosage", "kipimo"),
        ("legal", "en", "es", "plaintiff", "demandante"),
        ("legal", "en", "es", "defendant", "demandado"),
        ("legal", "en", "es", "affidavit", "declaración jurada"),
        ("legal", "en", "fr", "plaintiff", "demandeur"),
        ("legal", "en", "fr", "defendant", "défendeur"),
        ("legal", "en", "fr", "affidavit", "déclaration sous serment"),
        ("legal", "en", "sw", "plaintiff", "mlalamikaji"),
        ("legal", "en", "sw", "defendant", "mshtakiwa"),
        ("legal", "en", "sw", "affidavit", "kiapo"),
        ("technical", "en", "es", "firmware", "firmware"),
        ("technical", "en", "es", "bandwidth", "ancho de banda"),
        ("technical", "en", "es", "encryption", "cifrado"),
        ("technical", "en", "fr", "firmware", "micrologiciel"),
        ("technical", "en", "fr", "bandwidth", "bande passante"),
        ("technical", "en", "fr", "encryption", "chiffrement"),
        ("technical", "en", "sw", "firmware", "programu tegemezi"),
        ("technical", "en", "sw", "bandwidth", "upana wa mawimbi"),
        ("technical", "en", "sw", "encryption", "usimbaji"),
    ]
    table = sa.table(
        "glossary_terms",
        sa.column("domain", sa.String),
        sa.column("source_lang", sa.String),
        sa.column("target_lang", sa.String),
        sa.column("source_term", sa.String),
        sa.column("target_term", sa.String),
    )
    op.bulk_insert(
        table,
        [
            {
                "domain": d,
                "source_lang": sl,
                "target_lang": tl,
                "source_term": st,
                "target_term": tt,
            }
            for d, sl, tl, st, tt in seed
        ],
    )


def downgrade() -> None:
    op.drop_table("glossary_terms")
