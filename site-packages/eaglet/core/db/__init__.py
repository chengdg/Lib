
import settings

try:
    from mongoengine import connect
    for key,db_config in settings.DATABASES.items():
        try:
            if db_config['ENGINE'].lower() == "mongo":
                connect(db_config['NAME'], 
                        host=db_config['HOST'], 
                        alias=db_config['ALIAS'], 
                        username=db_config['USER'], 
                        password=db_config['PASSWORD'],
                        port=db_config.get('PORT',27017))
        except Exception, e:
            print(e)

    # if settings.MONGO:
        
    #     connect(settings.WEAPP_MONGO['DB'], host=settings.WEAPP_MONGO['HOST'])
    #     connect(settings.APP_MONGO['DB'], host=settings.APP_MONGO['HOST'], alias=settings.APP_MONGO['ALIAS'], username=settings.APP_MONGO['USERNAME'], password=settings.APP_MONGO['PASSWORD'])
except:
    print '[WARNING]: You have not installed mongoengine. App\'s data store will not be used. Please use "easy_install mongoengine" or "pip install mongoengine" to install it'