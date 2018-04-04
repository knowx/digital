from digital.api import hooks

# Pecan Application Configurations
app = {
    'root': 'digital.api.controllers.root.RootController',
    'modules': ['digital.api'],
    'debug': False,
    'hooks': [
        hooks.ContextHook(),
        hooks.NoExceptionTracebackHook(),
    ],
    'acl_public_routes': [
        '/',
        '/v1',
    ],
}