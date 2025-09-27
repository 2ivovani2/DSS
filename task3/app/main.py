import argparse, json
from db import connect, select_all, select_filter_one, select_filter_many, update_one, update_many_same, insert_one, insert_related_example, bulk_insert
from model_whitelist import TABLES

def pretty(x):
    import pprint; pprint.pprint(x, width=120)

def main():
    parser = argparse.ArgumentParser(description='Skins Marketplace')
    sub = parser.add_subparsers(dest='cmd', required=True)
    
    p_all = sub.add_parser('view-all'); p_all.add_argument('table', choices=TABLES.keys())
    p_one = sub.add_parser('view-where'); p_one.add_argument('table', choices=TABLES.keys()); p_one.add_argument('--col', required=True); p_one.add_argument('--val', required=True)
    
    p_many = sub.add_parser('view-where-many'); p_many.add_argument('table', choices=TABLES.keys()); p_many.add_argument('--json', required=True)
    p_up1 = sub.add_parser('update-one'); p_up1.add_argument('table', choices=TABLES.keys()); p_up1.add_argument('--id', type=int, required=True); p_up1.add_argument('--json', required=True)
    
    p_upmany = sub.add_parser('update-many-same'); p_upmany.add_argument('table', choices=TABLES.keys()); p_upmany.add_argument('--target-col', required=True); p_upmany.add_argument('--new-value', required=True); p_upmany.add_argument('--in-col', required=True); p_upmany.add_argument('--in-values', required=True)
    p_ins1 = sub.add_parser('insert-one'); p_ins1.add_argument('table', choices=TABLES.keys()); p_ins1.add_argument('--json', required=True)
    
    sub.add_parser('insert-related')
    
    p_bulk = sub.add_parser('bulk-insert'); p_bulk.add_argument('table', choices=TABLES.keys()); p_bulk.add_argument('--file', required=True)
    
    args = parser.parse_args()
    conn = connect()
    
    if not conn:
        print("Нет подключения к БД. Проверь .env/логин/пароль и попробуй снова."); raise SystemExit(1)
    
    if args.cmd == 'view-all': 
        pretty(select_all(conn, args.table, TABLES))
    
    elif args.cmd == 'view-where': 
        pretty(select_filter_one(conn, args.table, args.col, args.val, TABLES))
    
    elif args.cmd == 'view-where-many': 
        pretty(select_filter_many(conn, args.table, json.loads(args.json), TABLES))
    
    elif args.cmd == 'update-one': 
        pretty(update_one(conn, args.table, args.id, json.loads(args.json), TABLES))
    
    elif args.cmd == 'update-many-same': 
        pretty(update_many_same(conn, args.table, args.target_col, args.new_value, args.in_col, json.loads(args.in_values), TABLES))
    
    elif args.cmd == 'insert-one': 
        pretty(insert_one(conn, args.table, json.loads(args.json), TABLES))
    
    elif args.cmd == 'insert-related': 
        pretty(insert_related_example(conn))
    
    elif args.cmd == 'bulk-insert':
        with open(args.file, 'r', encoding='utf-8') as f: 
            rows = json.load(f)
    
        pretty(bulk_insert(conn, args.table, rows, TABLES))

if __name__ == '__main__':
    main()
