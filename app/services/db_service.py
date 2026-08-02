from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select, and_

from app.db.models import HotelModel, DestinationModel, ClusterModel

class DatabaseService:
    async def upsert_hotels(self, session: AsyncSession, parsed_hotels: List[Dict[str, Any]]) -> None:
        if not parsed_hotels:
            return
            
        unique_hotels = {}
        for hotel in parsed_hotels:
            name = hotel.get("name")
            link = hotel.get("link")
            
            if name and link:
                unique_key = f"{name}__{link}"
                unique_hotels[unique_key] = hotel
                
        valid_keys = {c.name for c in HotelModel.__table__.columns}
        
        for hotel_data in unique_hotels.values():
            clean_data = {k: v for k, v in hotel_data.items() if k in valid_keys}
            
            stmt = select(HotelModel).where(
                (HotelModel.name == clean_data.get("name")) & 
                (HotelModel.link == clean_data.get("link"))
            )
            result = await session.execute(stmt)
            existing_hotel = result.scalars().first()

            if existing_hotel:
                for key, value in clean_data.items():
                    setattr(existing_hotel, key, value)
                existing_hotel.last_updated = datetime.utcnow()
            else:
                new_hotel = HotelModel(**clean_data)
                session.add(new_hotel)
        
        await session.commit()

    async def upsert_destinations(self, session: AsyncSession, parsed_destinations: List[Dict[str, Any]]) -> None:
        if not parsed_destinations:
            return
            
        unique_dests = {}
        for dest in parsed_destinations:
            place_id = dest.get("place_id")
            if place_id:
                unique_dests[place_id] = dest 
                
        valid_keys = {c.name for c in DestinationModel.__table__.columns}
            
        for dest_data in unique_dests.values():
            clean_data = {k: v for k, v in dest_data.items() if k in valid_keys}
            
            place_id = clean_data.get("place_id")

            stmt = select(DestinationModel).where(DestinationModel.place_id == place_id)
            result = await session.execute(stmt)
            existing_dest = result.scalars().first()

            if existing_dest:
                for key, value in clean_data.items():
                    setattr(existing_dest, key, value)
                existing_dest.last_updated = datetime.utcnow()
            else:
                new_dest = DestinationModel(**clean_data)
                session.add(new_dest)

        await session.commit()

    async def get_cluster_restaurants(self, session: AsyncSession, lat: float, lng: float) -> List[Dict[str, Any]]:
        stmt = select(ClusterModel).where(
            and_(ClusterModel.grid_lat == lat, ClusterModel.grid_lng == lng)
        )
        result = await session.execute(stmt)
        cluster = result.scalars().first()
        
        if cluster and cluster.restaurant_place_ids:
            dest_stmt = select(DestinationModel).where(
                DestinationModel.place_id.in_(cluster.restaurant_place_ids)
            )
            dest_result = await session.execute(dest_stmt)
            restaurants = dest_result.scalars().all()
            
            res_list = []
            for r in restaurants:
                r_dict = r.__dict__.copy()
                r_dict.pop('_sa_instance_state', None)
                res_list.append(r_dict)
            return res_list
            
        return []

    async def upsert_cluster(self, session: AsyncSession, lat: float, lng: float, place_ids: List[str]) -> None:
        if not place_ids:
            return
            
        stmt = select(ClusterModel).where(
            and_(ClusterModel.grid_lat == lat, ClusterModel.grid_lng == lng)
        )
        result = await session.execute(stmt)
        existing_cluster = result.scalars().first()
        
        if existing_cluster:
            existing_cluster.restaurant_place_ids = place_ids
            existing_cluster.last_updated = datetime.utcnow()
        else:
            new_cluster = ClusterModel(
                grid_lat=lat, 
                grid_lng=lng, 
                restaurant_place_ids=place_ids
            )
            session.add(new_cluster)
        
        await session.commit()

db_service = DatabaseService()