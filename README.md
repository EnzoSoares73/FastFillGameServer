# Site e blog pessoal

Um site onde o usuário principal pode mostrar seu portfolio e competências, além de divulgar suas informações de contato e postar artigos.
## Começando

Como instalar e rodar esse projeto.

### Prerequisitos

As únicas tecnologias tecnologias necessárias são `Git` e `Docker`.

### Clonando

Crie uma cópia do código na sua máquina local com

```
git clone https://github.com/EnzoSoares73/meuSite.git
```
### Configurando variáveis de ambiente

Crie um arquivo chamado `.env` na raiz do seu projeto com o seguinte conteúdo:

```
DEBUG=1
SECRET_KEY=ALGUMACOISAFORTE
DJANGO_ALLOWED_HOSTS=*
USER=nomeuser
EMAIL=teste@teste.com
EMAIL_PASSWORD=senha
RECAPTCHA_SITE_KEY=aaaa
RECAPTCHA_PRIVATE_KEY=aaaa
DB_PASSWORD=senha
DB_USER=nomeuserqualquer
DB_NAME=meu_site
DB_HOST=db
```

Se quiser usar a funcionalidade de enviar emails pela página de contato, defina `EMAIL` e `EMAIL_PASSWORD` usando credenciais de email que dão suporte a `smtp` e substitua as credenciais `reCAPTCHA` por chaves obtidas através do site oficial. 

### Criando containers

Execute o script `scripts/rundjango.sh`. Se estiver usando linux, use `sudo`

### Definindo o usuário principal

Crie um usuário admin usando o comando:

```
docker exec meu_site python manage.py createsuperuser
```

O usuário deve ter o mesmo nome de `USER` em `.env`

## Feito com

* [PyCharm](https://www.jetbrains.com/pycharm/) - IDE usado
* [Django](https://www.djangoproject.com/) - WEB framework

## Autor

* **[Enzo Soares](https://github.com/EnzoSoares73)** 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details