from dynaconf import settings


print('# 1 all values in {} + {}: namespace of yaml file:'.format(
    settings.BASE_NAMESPACE_FOR_DYNACONF,
    settings.current_namespace))
assert settings.current_namespace == 'DEVELOPMENT'
print('HOST::', settings.HOST)
print('PORT:', settings.PORT)
print('USERNAME:', settings.USERNAME)
print('PASSWORD:', settings.PASSWORD)
print('LEVELS:', settings.LEVELS)
print('TEST_LOADERS:', settings.TEST_LOADERS)
print('MONEY:', settings.MONEY)
print('AGE:', settings.AGE)
print('ENABLED:', settings.ENABLED)
print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
print('WORKS:', settings.WORKS)

with settings.using_namespace('TESTING'):
    print('# 2 using {}: namespace values for context:'.format(
        settings.current_namespace))
    assert settings.current_namespace == 'TESTING'
    print('HOST::', settings.HOST)
    print('PORT:', settings.PORT)
    print('USERNAME:', settings.USERNAME)
    print('PASSWORD:', settings.PASSWORD)
    print('LEVELS:', settings.LEVELS)
    print('TEST_LOADERS:', settings.TEST_LOADERS)
    print('MONEY:', settings.MONEY)
    print('AGE:', settings.AGE)
    print('ENABLED:', settings.ENABLED)
    print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
    print('WORKS:', settings.WORKS)

print('# 3 back to default {}: namespace:'.format(settings.current_namespace))
assert settings.current_namespace == 'DEVELOPMENT'
print('HOST::', settings.HOST)
print('PORT:', settings.PORT)
print('USERNAME:', settings.USERNAME)
print('PASSWORD:', settings.PASSWORD)
print('LEVELS:', settings.LEVELS)
print('TEST_LOADERS:', settings.TEST_LOADERS)
print('MONEY:', settings.MONEY)
print('AGE:', settings.AGE)
print('ENABLED:', settings.ENABLED)
print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
print('WORKS:', settings.WORKS)

settings.namespace('testing')
print('# 4 Set to {}: namespace:'.format(settings.current_namespace))
assert settings.current_namespace == 'TESTING'
print('HOST::', settings.HOST)
print('PORT:', settings.PORT)
print('USERNAME:', settings.USERNAME)
print('PASSWORD:', settings.PASSWORD)
print('LEVELS:', settings.LEVELS)
print('TEST_LOADERS:', settings.TEST_LOADERS)
print('MONEY:', settings.MONEY)
print('AGE:', settings.AGE)
print('ENABLED:', settings.ENABLED)
print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
print('WORKS:', settings.WORKS)

settings.namespace()
print('# 5 back to default {}: namespace:'.format(settings.current_namespace))
assert settings.current_namespace == 'DEVELOPMENT'
print('HOST::', settings.HOST)
print('PORT:', settings.PORT)
print('USERNAME:', settings.USERNAME)
print('PASSWORD:', settings.PASSWORD)
print('LEVELS:', settings.LEVELS)
print('TEST_LOADERS:', settings.TEST_LOADERS)
print('MONEY:', settings.MONEY)
print('AGE:', settings.AGE)
print('ENABLED:', settings.ENABLED)
print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
print('WORKS:', settings.WORKS)


with settings.using_namespace('staging'):
    print('# 6 using {}: namespace values for context:'.format(
        settings.current_namespace))
    assert settings.current_namespace == 'STAGING'
    print('HOST::', settings.HOST)
    print('PORT:', settings.PORT)
    print('USERNAME:', settings.USERNAME)
    print('PASSWORD:', settings.PASSWORD)
    print('LEVELS:', settings.LEVELS)
    print('TEST_LOADERS:', settings.TEST_LOADERS)
    print('MONEY:', settings.MONEY)
    print('AGE:', settings.AGE)
    print('ENABLED:', settings.ENABLED)
    print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
    print('WORKS:', settings.WORKS)

print('# 7 back to default {}: namespace:'.format(settings.current_namespace))
assert settings.current_namespace == 'DEVELOPMENT'
print('HOST::', settings.HOST)
print('PORT:', settings.PORT)
print('USERNAME:', settings.USERNAME)
print('PASSWORD:', settings.PASSWORD)
print('LEVELS:', settings.LEVELS)
print('TEST_LOADERS:', settings.TEST_LOADERS)
print('MONEY:', settings.MONEY)
print('AGE:', settings.AGE)
print('ENABLED:', settings.ENABLED)
print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
print('WORKS:', settings.WORKS)

settings.namespace('staging')
assert settings.current_namespace == 'STAGING'
print('# 8 Set to {}: namespace:'.format(settings.current_namespace))
print('HOST::', settings.HOST)
print('PORT:', settings.PORT)
print('USERNAME:', settings.USERNAME)
print('PASSWORD:', settings.PASSWORD)
print('LEVELS:', settings.LEVELS)
print('TEST_LOADERS:', settings.TEST_LOADERS)
print('MONEY:', settings.MONEY)
print('AGE:', settings.AGE)
print('ENABLED:', settings.ENABLED)
print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
print('WORKS:', settings.WORKS)

settings.namespace()
print('# 9 back to default {}: namespace:'.format(settings.current_namespace))
print('HOST::', settings.HOST)
print('PORT:', settings.PORT)
print('USERNAME:', settings.USERNAME)
print('PASSWORD:', settings.PASSWORD)
print('LEVELS:', settings.LEVELS)
print('TEST_LOADERS:', settings.TEST_LOADERS)
print('MONEY:', settings.MONEY)
print('AGE:', settings.AGE)
print('ENABLED:', settings.ENABLED)
print('ENVIRONMENT:', settings.get('ENVIRONMENT'))
print('WORKS:', settings.WORKS)


assert settings.current_namespace == 'DEVELOPMENT'
