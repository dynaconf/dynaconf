# Extensão Flask


O Flask incentiva a substituição do atributo `config_class` por uma extensão que siga os padrões [definidos](http://flask.pocoo.org/docs/0.12/patterns/subclassing/).
Neste caso o Dynaconf fornece um substituto para o `app.config`, sendo assim o `app.config` passa ser uma instância de Dynaconf e usufrui das funcionalidades de gerenciamento de configuração.

## Inicialize a Extensão

Inicialize a extensão **FlaskDynaconf** para o seu `app`.

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app)
```

> Você pode opcionalmente usar `init_app`.

## Variáveis de Ambiente `FLASK_`

O `app.config` funcionará como uma instância `dynaconf.settings` e `FLASK_` será o prefixo global para exportar variáveis de ambiente.

Exemplo:

```bash
export FLASK_DEBUG=true              # app.config.DEBUG
export FLASK_INTVALUE=1              # app.config['INTVALUE']
export FLASK_MAIL_SERVER='host.com'  # app.config.get('MAIL_SERVER')
```

Você também pode definir um prefixo customizado para as variáveis de ambiente, assim como é feito na classe padrão (Dynaconf).

Exemplo:

```python
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
FlaskDynaconf(app, envvar_prefix="PEANUT")
```

Desta forma é possível exportar as variáveis usando o prefixo definido na declaração do objeto FlaskDynaconf.

```bash
export PEANUT_DEBUG=true              # app.config.DEBUG
export PEANUT_INTVALUE=1              # app.config['INTVALUE']
export PEANUT_MAIL_SERVER='host.com'  # app.config.get('MAIL_SERVER')
```

!!! info
    Na versão 3.1.7 era feita diferenciação entre maiúsculas e minúsculas na definição do `ENVVAR_PREFIX` e só aceitaria kwargs em letras maiúsculas (diferente de `Dynaconf(envvar_prefix)`). A partir da versão X.X.X, os kwargs não devem diferenciar maiúsculas de minúsculas para melhorar a consistência entre as extensões Dynaconf e Flask/Django, mantendo a compatibilidade com versões anteriores.

## Arquivos de Configuração

Você também pode ter seus arquivos de configuração para a sua aplicação Flask. Coloque os arquivos `settings.toml` e `.secrets.toml`, no diretório raiz (mesmo lugar onde é executado `flask run`) e então os ambientes da aplicação `[default]`, `[development]` e `[production]`.

Use a variável `FLASK_ENV` para alternar entre os ambientes definidos no arquivo de configuração. Por exemplo, definir `FLASK_ENV=development` fará com que a aplicação opere com os valores definidos do ambiente de desenvolvimento, já `FLASK_ENV=production` substituirá para os
valores definidos para o ambiente de produção.

> **IMPORTANTE**: Para usar `$ dynaconf` CLI a varável `FLASK_APP` deve ser definida previamente.

Se você não quer criar os seus arquivos de configuração manualmente considere dar uma olhada em [CLI](cli.md)

## Carregando Extensões Flask Dinamicamente

Você pode pedir ao Dynaconf para carregar suas extensões Flask dinamicamente, desde que elas sigam os padrões das extensões convencionada pelo Flask.

O único requisito é que a extensão deva ser do tipo `callable` e deve receber o `app` como primeiro argumento (`flask_admin:Admin` ou `custom_extension.module:instance.init_app`),  e por fim a extensão deve ser

The only requirement is that the extension must be a `callable` that accepts `app` as first argument. e.g: `flask_admin:Admin` or `custom_extension.module:instance.init_app` and of course the extension must be in Python namespace to be imported.

Para que a extensão seja inicializada basta usar uma referência para o [*entry point*](https://packaging.python.org/specifications/entry-points/), por exemplo: "flask_admin:Admin" or "extension.module:instance.init_app".

Definição do arquivo `settings.toml`

```toml
[default]
EXTENSIONS = [
  "flask_admin:Admin",
  "flask_bootstrap:Bootstrap",
  "custom_extension.module:init_app"
]
```

No arquivo `app.py`:
```py
from flask import Flask
from dynaconf import FlaskDynaconf

app = Flask(__name__)
flask_dynaconf = FlaskDynaconf(app, extensions_list="EXTENSIONS")
```
No trecho acima ele irá carregar todas as extensões Flask listadas na chave `EXTENSIONS` dentro do arquivo de configuração.

Você também pode carregar as configurações usando *lazy loading*.

```py
# at any point in your app startup
app.config.load_extensions()
```

Opcionalmente você pode chamar `load_extensions(key="OTHER_NAME")` apontando para a sua lista de extensões.

Outra forma de carregar as extensões é por meio de variáveis de ambiente, por exemplo:

```bash
# .env
export FLASK_EXTENSIONS="['flask_admin:Admin']"
```

As extensões serão carregadas em ordem.

### Extensões de desenvolvimento

É possível carregar extensões de desenvolvimento usadas somente em ambiente de desenvolvimento.

```toml
[default]
EXTENSIONS = [
  "flask_admin:Admin",
  "flask_bootstrap:Bootstrap",
  "custom_extension.module:init_app"
]

[development]
EXTENSIONS = [
  "dynaconf_merge",
  "flask_debugtoolbar:DebugToolbar"
]
```

### Problemas Frequentes

Caso você encontre um problema no momento do carregamento das variáveis do arquivo `.env` ou na importação do app, ou create_app,
é recomendado desativar o suporte do Flask para dotenv.

```bash
export FLASK_SKIP_DOTENV=1
```
