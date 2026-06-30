"""Role A — memory/debug endpoints (the memory-view feed + manual forget)."""
from fastapi import APIRouter, Depends
from backend.deps import get_memory
from contracts.memory_interface import MemoryService

router = APIRouter()


@router.get("/{player_id}/graph")
async def memory_graph(player_id: str, mem: MemoryService = Depends(get_memory)):
    return await mem.get_graph(player_id)


@router.post("/{player_id}/forget")
async def forget(player_id: str, mem: MemoryService = Depends(get_memory)):
    await mem.forget(player_id)
    return {"forgotten": player_id}
