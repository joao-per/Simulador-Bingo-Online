# Simulador de Bingo!
Este projeto foi desenvolvido no âmbito do projeto final da cadeira **Linguagens de Programação** , do curso de **Engenharia Informática** .

---


## Descrição 
O **Simulador de Bingo**  é uma aplicação interativa que permite jogar Bingo "online" de forma divertida e funcional. O projeto implementa funcionalidades de: 
- **Host e Jogadores** : escolha o papel de Host para organizar o jogo ou entre como jogador para competir.
 
- **Cartões Personalizados** : cada jogador recebe um cartão de Bingo exclusivo.
 
- **Regras do Bingo** : celebra o primeiro jogador a fazer uma linha e, posteriormente, o primeiro a completar o Bingo.
 
- **Histórico e Log de Eventos** : armazena os resultados de cada partida e permite consultar os acontecimentos relevantes, como vencedores e concorrentes.
 
- **Interface Atraente** : uma interface gráfica estilizada e intuitiva para tornar o jogo ainda mais agradável.


---


## Funcionalidades 
 
- **Host** :
  - Gere o jogo.

  - Realiza o sorteio dos números.

  - Visualiza o histórico e o log de eventos.
 
- **Jogador** :
  - Recebe um cartão de Bingo.

  - Visualiza os números sorteados e marca automaticamente o seu cartão.

  - Compete para alcançar a primeira linha e o Bingo completo.
 
- **Banco de Dados** : 
  - Armazena informações detalhadas de cada partida, incluindo:
    - Vencedor da primeira linha.

    - Vencedor do Bingo.

    - Lista de concorrentes.

    - Número total de sorteios.


---


## Estrutura do Projeto 
 
1. **Interface Gráfica (GUI)** : 
  - Desenvolvida com **Tkinter** .

  - Contém botões interativos, visualização do cartão e atualizações em tempo real.
 
2. **Servidor (Server)** :
  - Gerencia a comunicação entre os jogadores.

  - Garante que os números sorteados não se repitam.

  - Registra os resultados no banco de dados.
 
3. **Cliente (Client)** :
  - Conecta os jogadores ao servidor.

  - Atualiza o estado do jogo para cada participante.
 
4. **Banco de Dados** : 
  - Utiliza **SQLite3**  para persistir os resultados.


---


## Requisitos do Sistema 

- Python 3.10 ou superior.
 
- Bibliotecas: 
  - `tkinter`
 
  - `sqlite3`


---


## Como Executar 

1. Clone o repositório para o seu computador.

2. Instale as dependências necessárias, caso ainda não as tenha.
 
3. Inicie o servidor:

```bash
python server.py
```
 
4. Inicie a interface gráfica:

```bash
python main.py
```
 
5. Escolha entre ser **Host**  ou **Jogador** .


---


## Créditos 
Desenvolvido por: **Beatriz Ferreira**,
Cadeira: **Linguagens de Programação**, 
Universidade Lusófona do Porto, Engenharia Informática
