"""One-off: delete conversation rows that contain the invalid 'image_ref' placeholder."""
import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import aiosqlite

DB = Path(__file__).parent.parent / "data" / "app.db"

async def main():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "DELETE FROM conversations WHERE content LIKE ?", ("%image_ref%",)
        )
        await db.commit()
        print(f"Deleted {cur.rowcount} bad row(s)")

asyncio.run(main())
