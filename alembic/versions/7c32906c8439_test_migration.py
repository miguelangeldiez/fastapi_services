from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '7c32906c8439'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Eliminar las filas existentes
    op.execute("DELETE FROM posts")

    # Agregar la columna con NOT NULL
    op.add_column('posts', sa.Column('user_id', UUID(as_uuid=True), nullable=False))


def downgrade():
    # Eliminar la columna en caso de revertir la migración
    op.drop_column('posts', 'user_id')