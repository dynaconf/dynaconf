# Feature flag system

## feature toggles

Feature flagging is a system to dynamically toggle features in your
application based in some settings value.

The advantage of using it is to perform changes on the fly without the need to redeploy ou restart the application.

Learn more on how to design your program using Feature Flags: [http://martinfowler.com/articles/feature-toggles.html](http://martinfowler.com/articles/feature-toggles.html)

Example:

Lets say you have 2 versions of your app dashboard and you want to serve the new version only for premium users.

write flags to [redis](external_storages.html)

```
$ dynaconf write redis -s NEWDASHBOARD=true -e premiumuser
```

In your program do:

```python
usertype = 'premiumuser'  # assume you loaded it as part of your auth

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
