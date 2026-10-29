from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.events import EventsModel
from schemas.entities import SGitHubEvent

class EventsRepository:
    @classmethod
    async def add_one(cls, event_id:str, event_type: str, data: SGitHubEvent, session: AsyncSession) -> EventsModel:
    # EventsRepository.add_one(event_id=event_id, event_type=event_type, data=payload, session=session)

        #print("Добавляю в базу данных...")
        action = data.action
        sender = data.sender.login
        repository_full_name = data.repository.full_name
        validated_payload = data.model_dump()        
        
        event = EventsModel(event_id=event_id,
                            event_type=event_type,
                            action=action,
                            sender=sender,
                            repository_full_name=repository_full_name,
                            payload=validated_payload)
        
        session.add(event)
        await session.commit()
        await session.refresh(event)
        
        return event

    @classmethod
    async def find_all(cls, session: AsyncSession):
        query = select(EventsModel)
        
        result = await session.execute(query)
        
        events_models = result.scalars().all()
        return events_models