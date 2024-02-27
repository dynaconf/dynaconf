# Início Rápido com Dynaconf

<p style="align-content: center">
  <a href="https://dynaconf.com"><img src="img/logo_400.svg?sanitize=true" alt="Dynaconf"></a>
</p>
<p style="align-content: center">
    <em>Gereciamento de Configurações para Python.</em>
</p>

<p style="align-content: center"><a href="/LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square"></a> <a href="https://pypi.python.org/pypi/dynaconf"><img alt="PyPI" src="https://img.shields.io/pypi/v/dynaconf.svg"></a><a href="https://github.com/dynaconf/dynaconf/actions/workflows/main.yml"><img src="https://github.com/dynaconf/dynaconf/actions/workflows/main.yml/badge.svg"></a><a href="https://codecov.io/gh/dynaconf/dynaconf"><img alt="codecov" src="https://codecov.io/gh/dynaconf/dynaconf/branch/master/graph/badge.svg"></a> <a href="https://www.codacy.com/gh/dynaconf/dynaconf/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dynaconf/dynaconf&amp;utm_campaign=Badge_Grade"><img src="https://app.codacy.com/project/badge/Grade/3fb2de98464442f99a7663181803b400"/></a> <img alt="GitHub Release Date" src="https://img.shields.io/github/release-date/dynaconf/dynaconf.svg"> <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/dynaconf/dynaconf.svg"> <a href="https://github.com/dynaconf/dynaconf/discussions"><img alt="Discussions" src="https://img.shields.io/badge/discussions-forum-yellow.svg?logo=googlechat"></a> <a href="https://github.com/rochacbruno/learndynaconf"><img alt="Demo" src="https://img.shields.io/badge/demo-learn-blue.svg?logo=gnubash"></a></p>


> **DICA** Você pode ver uma exmplo funcional aqui (em inglês): https://github.com/rochacbruno/learndynaconf

## Recursos

- Inspirado no **[12-factor application guide](https://12factor.net/pt_br/config)**
- **Gerenciamento de configurações** (valores padrão, validação, análise (parsing), modelagem (templating))
- Proteção de **informações sensíveis** (passwords/tokens)
- Múltiplos **formatos de arquivos** `toml|yaml|json|ini|py` e, também, carregadores (loaders) personalizáveis.
- Suporte total para **variáveis de ambiente** para substituir as configurações existentes (incluindo suporte a dotenv).
- Sistema em camadas opcionais para **vários ambientes** `[padrão, desenvolvimento, teste, produção]` (também chamado multiplos perfis)
- Suporte nativo para **Hashicorp Vault** e **Redis** para configurações e amarzenamento de segredos.
- Extensões nativas para **Django**, **Flask** e **fastAPI** web framewors.
- **CLI** para operações comuns tais como `init, list, write, validate, export`.

## Instalação

### Instalando via [pypi](https://pypi.org/project/dynaconf)

```bash
pip install dynaconf
```
### Initialize Dynaconf on your project

???+ "Usando somente Python"

    #### Usando somente Python

    No diretório raiz de seu projeto execute o comando `dynaconf init`

    ```bash hl_lines="2"
    cd path/to/your/project/
    dynaconf init -f toml
    ```
    A saída do comando deverá ser:

    ```plain

    ⚙️  Configuring your Dynaconf environment
    ------------------------------------------
    🐍 The file `config.py` was generated.

    🎛️  settings.toml created to hold your settings.

    🔑 .secrets.toml created to hold your secrets.

    🙈 the .secrets.* is also included in `.gitignore`
    beware to not push your secrets to a public repo.

    🎉 Dynaconf is configured! read more on https://dynaconf.com
    ```

    > ℹ️ Você pode escolher `toml|yaml|json|ini|py` em `dynaconf init -f <fileformat>`,  **toml** é o formato padrão e o mais **recomendado** para configurações.

    O comando `init` do Dynaconf cria os seguintes arquivos

    ```plain
    .
    ├── config.py       # No qual você importa seu objeto de configuração (obrigatório)
    ├── .secrets.toml   # Arquivo com dados sensíveis como senhas e tokesn (opctional)
    └── settings.toml   # Configurações da aplicação (opcional)
    ```

    === "your_program.py"
        Em seu código você importa e usa o objeto **settings**, este é importado do arquivo **config.py**
        ```python
        from config import settings

        assert settings.key == "value"
        assert settings.number == 789
        assert settings.a_dict.nested.other_level == "nested value"
        assert settings['a_boolean'] is False
        assert settings.get("DONTEXIST", default=1) == 1
        ```

    === "config.py"
        Neste arquivo a nova instância do objeto *setings* de **Dynaconf** é inicializada e configurada.
        ```python
        from dynaconf import Dynaconf

        settings = Dynaconf(
            settings_files=['settings.toml', '.secrets.toml'],
        )
        ```
        Mais opções são descritas em [Dynaconf Configuration](configuration.md)

    === "settings.toml"
        **Opcionalmente** armazene as configurações em um arquivo (ou em múltiplos arquivos)
        ```toml
        key = "value"
        a_boolean = false
        number = 1234
        a_float = 56.8
        a_list = [1, 2, 3, 4]
        a_dict = {hello="world"}

        [a_dict.nested]
        other_level = "nested value"
        ```
        Mais detalhes em [Settings Files](settings_files.md)

    === ".secrets.toml"
        **Opcionalmente** armazene dados sensíveis em um único arquivo local chamado `.secrets.toml`
        ```toml
        password = "s3cr3t"
        token = "dfgrfg5d4g56ds4gsdf5g74984we5345-"
        message = "This file doesn't go to your pub repo"
        ```

        > ⚠️ O comando `dynaconf init` coloca o `.secrets.*` em seu `.gitignore` evitando que o mesmo seja exposto no repositório público mas é sua responsabilidade mantê-lo em seu ambiente local, também é recomendado que os ambientes de produção utilizem o suporte nativo para o serviço da Hashicorp Vault para senhas e tokens.

        ```ini
        # Segredos não vão para o repositório público
        .secrets.*
        ```

        Leia mais em [Secrets](secrets.md)

    === "env vars"
        **Opcionalmente** use variáveis de ambiente com prefixos. (arquivos `.env` também são suportados)

        ```bash
        export DYNACONF_NUMBER=789
        export DYNACONF_FOO=false
        export DYNACONF_DATA__CAN__BE__NESTED=value
        export DYNACONF_FORMATTED_KEY="@format {this.FOO}/BAR"
        export DYNACONF_TEMPLATED_KEY="@jinja {{ env['HOME'] | abspath }}"
        ```

    ---

    > ℹ️ Você pode criar os arquivos em vez de utilizar o comando `dynaconf init` e dar qualquer nome que queira em vez do padrão `config.py` (o arquivo deve estar em seu `python path` para ser importado)
