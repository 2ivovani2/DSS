TABLES = {
  'users': ['id','username','email','created_at'],
  'weapons': ['id','name','wclass'],
  'skins': ['id','weapon_id','name','rarity','collection'],
  'items': ['id','skin_id','owner_id','wear','pattern','stattrak','stickers','created_at'],
  'listings': ['id','item_id','seller_id','price','currency','status','created_at'],
  'orders': ['id','listing_id','buyer_id','price','purchased_at'],
}
