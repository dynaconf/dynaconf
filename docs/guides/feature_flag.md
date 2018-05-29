# Feature flag system

## feature toggles

Feature flagging is a system to dynamically toggle features in your
application based in some settings value.

Learn more at: http://martinfowler.com/articles/feature-toggles.html

Example:

write flags to redis
```
$ dynaconf write redis -s NEWDASHBOARD=1 -e premiumuser
```

meaning: Any premium user has NEWDASHBOARD feature enabled!

In your program do:

```python
usertype = 'premiumuser'  # assume you loaded it from your database

# user has access to new dashboard?
if settings.flag('newdashboard', usertype):
    activate_new_dashboard()
else:
    # User will have old dashboard if not a premiumuser
    activate_old_dashboard()
```

The value is ensured to be loaded fresh from redis server so features can be enabled or 
disabled at any time without the need to redeploy.

It also works with file settings but the recommended is redis
as the data can be loaded once it is updated.
