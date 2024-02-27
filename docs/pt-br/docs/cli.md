

## configurando instancias

Todo comando (com exceção do init) requer uma Instância que pode ser passada usando o parâmetro `-i` ou por variável de ambiente com `export INSTANCE_FOR_DYNACONF`

## O dynaconf CLI (Interface de Linha de Comando)

O comando `$ dynaconf -i config.settings` do cli provê alguns comandos bem úteis

> **IMPORTANTE** caso usem [Flask Extension](flask.md) a variável de ambiente `FLASK_APP` deve ser definda para usar o CLI, e caso usem [Django Extension](django.md) a variável `DJANGO_SETTINGS_MODULE` deve estar definida.

### dynaconf --help

```bash
Uso: dynaconf [OPÇÕES] COMMAND [ARGS]...

  Dynaconf - Command Line Interface

  Documentation: https://dynaconf.com/

Opções:
  --version            Mostra a versão do dynaconf
  --docs               Abre a documentação no navegador
  --banner             Mostra um banner maneiro
  -i, --instance TEXT  Define a instância customizada do LazySettings
  --help               Mostra essa mensagem e sai.

Commands:
  get       Retorna o valor bruto de uma chave de configuração
  init      Inicia um projeto dynaconf, por padrão cria um settings.toml ...
  list      Lita todos os valores de configuração definidos pelo usuário se `--all` é passado ...
  validate  Valida as configurações do Dynaconf baseado em regras definidas em...
  write     Escreve dados para o recurso específico
```

### dynaconf init

Use o comando init para facilmente iniciar a configuração de sua aplicaçãoto, tendo o dynaconf instalado vá para o diretório raiz de sua aplicação e execute:

```
$ dynaconf init -v key=value -v foo=bar -s token=1234
```

O comando acima criará no diretório corrente:

`settings.toml`

```ini
KEY = "value"
FOO = "bar"
```

also `.secrets.toml`

```ini
TOKEN = "1234"
```

Bem como incluirá no arquivo `.gitignore` para que seja ignorado o arquivo `.secrets.toml`, como descrito abaixo:

```ini
# Ignore dynaconf secret files
.secrets.*
```

> Reomenda-se que para dados sensíveis em produção use[Vault Server](secrets.md)

```
Uso: dynaconf init [OPÇÕES]

  Inicia um projeto dynaconf que por padrão cria um settings.toml e um
  .secrets.toml para os ambientes [default|development|staging|testing|production|global].

  O formato dos arquivo pode ser alterado passando --format=yaml|json|ini|py.

  Esse comando deve ser executado no diretório raiz do projeto o pode-se passar
  --path=/myproject/root/folder.

  O --env/-e está depreciado ( mantido por compatibilidade, mas deve evitar o uso)

Opções:
  -f, --format [ini|toml|yaml|json|py|env]
  -p, --path TEXT                 o padrão é o diretório corrente
  -e, --env TEXT                  Define o ambiente de trabalho no arquivo `.env`
  -v, --vars TEXT                 valores extras a serem gravados no arquivo de settings, ex.:
                                  `dynaconf init -v NAME=foo -v X=2

  -s, --secrets TEXT              valores sensíveis a serem escritos no arquivo .secrets
                                  ex.: `dynaconf init -s TOKEN=kdslmflds

  --wg / --no-wg
  -y
  --django TEXT
  --help                          Mostra essa mensagem e sai.
```

Observe que a opção `-i`/`--instance` não pode ser usada com `init`, pois `-i` deve apontar para uma instância existente das configurações.


### Dynaconf get

Pega o valor bruto para uma única chave

```bash
Uso: dynaconf get [OPÇÕES ] KEY

  Retorna o valor bruto para a KEY na configuração

Opções:
  -d, --default TEXT  Valor padrão se a configuração não existir
  -e, --env TEXT      Filtra o ambiente (env) para pegar os valores do ambiente especificado
  -u, --unparse       Não analisa (unparse) os dados pela adição de marcadores como: @none, @int etc..
  --help              Mostra essa mensagem e sai.
```

Exemplo:

```bash
export FOO=$(dynaconf get DATABASE_NAME -d 'default')
```


### dynaconf list

Lista todos os parâmetros definidos e, opcionalmente, exporta para um arquivo JSON.

```
Uso: dynaconf list [OPÇÕES]

  Lista todos os valores de configuração definidos pelo usuário e se `--all` for passado
  mostra, também, as variáveis internas do dynaconf.

Opçẽos:
  -e, --env TEXT     Filtra o ambiente (env) para pegar os valores
  -k, --key TEXT     Filtra por uma única chave (key)
  -m, --more         Pagina o resultado ao estilo mais|menos (more|less)
  -l, --loader TEXT  um identificador de conversor (loader) para filtar ex.: toml|yaml
  -a, --all          Mostra as configurações internas do dynaconf?
  -o, --output FILE  Filepath para gravar os valores listados num arquivo JSON
  --output-flat      O arquivo de saída é plano (flat) (i.e., não inclui o nome ambiente [env])
  --help             Mostra essa mensagem e sai.
```

#### Exportanto o ambiente atual como um arquivo

```bash
dynaconf list -o path/to/file.yaml
```

O comando acima exportará todos os itens mostrados por `dynaconf list` para o format desejado o qual é inferido pela extensão do arquivo em `-o`, formatos suportados são: `yaml, toml, ini, json, py`

Quando se usa `py` pode-se querer uma saída plana (flat) (sem estar aninhada internamente pelo nome do ambiente (env))

```bash
dynaconf list -o path/to/file.py --output-flat
```

### dynaconf write

```
Uso: dynaconf write [OPÇÕES] [ini|toml|yaml|json|py|redis|vault|env]

  Escreve os dados dem uma fonte específica

Opções:
  -v, --vars TEXT     Par chave=valor que será escrito no settings ex.:
                      `dynaconf write toml -e NAME=foo -e X=2

  -s, --secrets TEXT  Par chave=segredo que será escrito no .secrets ex:
                      `dynaconf write toml -s TOKEN=kdslmflds -s X=2

  -p, --path TEXT     Diretório/Arquivo no qual será escrito, sendo o padrão para diretório-atual/settings.{ext}
  -e, --env TEXT      Ambiente para o qual o valor será registrado o padrão é o DEVELOPMENT, para arquivos de recursos
                      externos como o Redis e o Vault será
                      DYNACONF ou o valor configurado na variável $ENVVAR_PREFIX_FOR_DYNACONF

  -y
  --help              Mostra essa mensagem e sai.
```

### dynaconf validate

> **Novo desde a versão 1.0.1**

Iniciado na versão 1.0.1, é possível definir validadores no arquivo **TOML** chamado **dynaconf_validators.toml** colocado na mesma pasta do seu arquivo settings.

`dynaconf_validators.toml` equivalente ao descrito acima

```ini
[default]

version = {must_exist=true}
name = {must_exist=true}
password = {must_exist=false}

  [default.age]
  must_exist = true
  lte = 30
  gte = 10

[production]
project = {eq="hello_world"}
```

Para executar a validação use o comando abaixo:

```
$ dynaconf -i config.settings validate
```

A validação ocorrendo sem problemas retornará status 0 (sucesso) e, por isso, o comando pode ser usado na pipeline de CI/CD/Deploy.

### dynaconf --version

Retorna a versão do dynaconf instalada

```
$ dynaconf -i config.settings --version
1.0.0
```

### dynaconf --docs

Abre a documentação do Dynaconf no navegador padrão do sistema.


### dynaconf --banner

Imprime esse bonito baner feito em ascci no terminal :)

```
$ dynaconf -i config.settings --banner

██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝

Learn more at: http://github.com/dynaconf/dynaconf
```
