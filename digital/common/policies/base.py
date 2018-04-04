from oslo_policy import policy

ROLE_ADMIN = 'rule:context_is_admin'
RULE_ADMIN_OR_OWNER = 'rule:admin_or_owner'
RULE_ADMIN_API = 'rule:admin_api'
RULE_ADMIN_OR_USER = 'rule:admin_or_user'

rules = [
    policy.RuleDefault(
        name='context_is_admin',
        check_str='role:admin'
    ),
    policy.RuleDefault(
        name='admin_or_owner',
        check_str='is_admin:True or project_id:%(project_id)s'
    ),
    policy.RuleDefault(
        name='admin_api',
        check_str='rule:context_is_admin'
    ),
    policy.RuleDefault(
        name='admin_or_user',
        check_str='is_admin:True or user_id:%(user_id)s'
    ),
]


def list_rules():
    return rules
