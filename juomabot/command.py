import argparse
import os

from juomabot import api
from juomabot.excs import Problem

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'hackme')


ap = argparse.ArgumentParser(prog='juomabot', add_help=False)
ap.add_argument('-p', '--password', default=None)
ap.add_argument('-h', '--help', dest='action', action='store_const', const='help')
ap.add_argument('-l', '--pricelist', dest='action', action='store_const', const='pricelist')
ap.add_argument('-a', '--add-product', dest='action', action='store_const', const='add_product', help='add a new product')
ap.add_argument('-e', '--edit-product', dest='action', action='store_const', const='edit_product', help='edit a named product')
ap.add_argument('-t', '--toggle-product', dest='action', action='store_const', const='toggle_product', help='enable or disable a product')
ap.add_argument('-s', '--stats', dest='action', action='store_const', const='stats', help='see your personal stats')
ap.add_argument('-b', '--billing-stats', dest='action', action='store_const', const='billing_stats', help='see billing statistics in CSV form')
ap.add_argument('-B', '--bill', dest='bill_sig', default=None, help='bill a billing statistics report')
ap.add_argument('--price', dest='price', default=None, help='price for a new or edited product')
ap.add_argument('params', nargs='*', help='other params, depends on the command. usually the drink name.')

regular_commands = {
    'add_purchase': lambda args: api.add_purchase(args.sender, args.params),
    'pricelist': lambda args: api.get_price_list(),
    'stats': lambda args: api.get_own_stats(sender=args.sender),
}

admin_commands = {
    'add_product': lambda args: api.add_product(name=args.params, price=args.price),
    'edit_product': lambda args: api.edit_product(name=args.params, price=args.price),
    'toggle_product': lambda args: api.toggle_product_visible(name=args.params),
    'billing_stats': lambda args: api.billing_stats(),
    'bill': lambda args: api.bill(bill_sig=args.bill_sig, biller=args.sender),
}

def _dispatch_command(action, args):
    if action in admin_commands:
        if (args.password == ADMIN_PASSWORD):
            return admin_commands[action](args)
        else:
            raise Problem(
                'Sorry, you need to be an admin to do %s. Use the `-p` switch to enter a password.' % action,
                code='not-an-admin'
            )

    return regular_commands[action](args)


def run_command(sender, text):
    """
    Run a command and return the response text (or raise a Problem)

    :param sender: The sender username.
    :type sender: str
    :param text: The command (after the slash command; as sent by Slack)
    :type text: str
    :return: Response text
    :rtype: str
    :raises Problem: if something goes awry.
    """
    args = ap.parse_args(text.replace('—', '--').split())
    action = getattr(args, 'action', None) or 'add_purchase'
    if action == 'help':
        return ':information_desk_person: Here\'s some help for you!\n```\n%s\n```' % ap.format_help()
    args.params = (' '.join(args.params)).strip(" \'")
    args.sender = sender

    if args.bill_sig:
        action = 'bill'

    return _dispatch_command(action, args)
