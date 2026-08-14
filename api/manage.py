import argparse
import asyncio
import secrets
import string
import sys
import logging

from app.db.connection import init_pool, close_pool
from app.db import users as db_users
from app.security import hash_password
import asyncpg

# Configure logging to print to console
logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")
logger = logging.getLogger("bough-cli")

def generate_temp_password() -> str:
    """Generates a random secure password."""
    return secrets.token_urlsafe(16)

async def create_user(username: str, password: str | None):
    if not password:
        password = generate_temp_password()
        logger.info(f"Generated password: {password}")
        
    hashed = hash_password(password)
    try:
        user_id = await db_users.create_user(username, hashed)
        logger.info(f"Success: Created user '{username}' with ID: {user_id}")
    except asyncpg.UniqueViolationError:
        logger.error(f"Error: Username '{username}' already exists.")

async def reset_password(username: str, password: str | None):
    user = await db_users.fetch_user_by_username(username)
    if not user:
        logger.error(f"Error: User '{username}' not found.")
        return
        
    if not password:
        password = generate_temp_password()
        logger.info(f"Generated password: {password}")
        
    hashed = hash_password(password)
    await db_users.update_password(user['id'], hashed)
    # Optional: force logout everywhere by deleting sessions
    await db_users.delete_all_sessions_for_user(user['id'])
    logger.info(f"Success: Password reset for '{username}'. All sessions revoked.")

async def disable_user(username: str):
    user = await db_users.fetch_user_by_username(username)
    if not user:
        logger.error(f"Error: User '{username}' not found.")
        return
        
    await db_users.set_user_active_status(user['id'], False)
    await db_users.delete_all_sessions_for_user(user['id'])
    logger.info(f"Success: User '{username}' disabled and logged out.")

async def enable_user(username: str):
    user = await db_users.fetch_user_by_username(username)
    if not user:
        logger.error(f"Error: User '{username}' not found.")
        return
        
    await db_users.set_user_active_status(user['id'], True)
    logger.info(f"Success: User '{username}' enabled.")

async def list_users():
    users = await db_users.fetch_all_users()
    if not users:
        logger.info("No users found.")
        return
        
    # Print a simple table
    print(f"{'ID':<36} | {'Username':<20} | {'Active':<7} | {'Created At'}")
    print("-" * 80)
    for u in users:
        print(f"{str(u['id']):<36} | {u['username']:<20} | {str(u['is_active']):<7} | {u['created_at']}")

async def run_cli(args):
    await init_pool()
    try:
        if args.command == 'create-user':
            await create_user(args.username, args.password)
        elif args.command == 'reset-password':
            await reset_password(args.username, args.password)
        elif args.command == 'disable-user':
            await disable_user(args.username)
        elif args.command == 'enable-user':
            await enable_user(args.username)
        elif args.command == 'list-users':
            await list_users()
        else:
            logger.error("Unknown command. Use --help for usage.")
    finally:
        await close_pool()

def main():
    parser = argparse.ArgumentParser(description="BOUGH Account Management CLI", add_help=False)
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    subparser_map = {}

    # Create
    p_create = subparsers.add_parser('create-user', help='Create a new user account', add_help=False)
    p_create.add_argument('username', help='The username')
    p_create.add_argument('password', nargs='?', help='The password (auto-generated if omitted)')
    subparser_map['create-user'] = p_create

    # Reset
    p_reset = subparsers.add_parser('reset-password', help='Reset a user\'s password', add_help=False)
    p_reset.add_argument('username', help='The username')
    p_reset.add_argument('password', nargs='?', help='The new password (auto-generated if omitted)')
    subparser_map['reset-password'] = p_reset

    # Disable
    p_disable = subparsers.add_parser('disable-user', help='Disable a user account', add_help=False)
    p_disable.add_argument('username', help='The username')
    subparser_map['disable-user'] = p_disable

    # Enable
    p_enable = subparsers.add_parser('enable-user', help='Enable a user account', add_help=False)
    p_enable.add_argument('username', help='The username')
    subparser_map['enable-user'] = p_enable

    # List
    subparsers.add_parser('list-users', help='List all user accounts', add_help=False)

    # Help
    p_help = subparsers.add_parser('help', help='Show help for a specific command', add_help=False)
    p_help.add_argument('help_command', nargs='?', help='The command to get help for')

    args = parser.parse_args()
    
    if args.command == 'help':
        if args.help_command and args.help_command in subparser_map:
            subparser_map[args.help_command].print_help()
        else:
            parser.print_help()
        return

    try:
        asyncio.run(run_cli(args))
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)

if __name__ == "__main__":
    main()