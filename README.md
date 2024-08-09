# 7J
<img src="https://github.com/jms3471/7J/blob/main/assets/icon.png" alt="Logo 7J" width="200" height="auto">

## Objetivo e Público-Alvo

**7J**, acrônimo para ***Software Educacional Economizador de Tempo do Jonathan***, tem como objetivo facilitar o dimensionamento de eixos de transmissão, simplificando esse processo para os alunos de graduação em Engenharia Mecânica.  

O aplicativo visa tornar o conteúdo mais acessível e compreensível para os estudantes, eliminando a necessidade de realizar cálculos extensos e, assim, tornando o tópico mais claro.


> [!WARNING]  
> Este software vem com absolutamente **NENHUMA GARANTIA**, sendo projetado para atender estudantes em meio estritamente acadêmico teórico. Qualquer uso fora desse contexto está por sua conta e risco. Para mais informações, consulte a [licença](#licença).

## Como usar

- Baixar o arquivo executável  (main.exe) localizado **[AQUI!](https://github.com/jms3471/7J/releases/tag/v.0)**  

- Ou clonar o repositório e instalar os pacotes necessários, conforme instruções abaixo:  

> [!IMPORTANT]  
> **Você precisa ter o Python (v3.11+) instalado!**


1. Após baixar o repositório, crie um ambiente virtual dentro dele.
    ```
    python -m venv venv
    ```

2. Ative o ambiente.
    > **Windows**  
     ```
    .\venv\Scripts\activate
    ```

    >**Linux/Mac**  
    ```bash
    source venv/bin/activate
    ```

3. Instale as bibliotecas necessárias.
    ```
    pip install -r requirements.txt
    ```

4. Finalizado o item anterior, basta rodar:  
    ```
    flet run main.py
    ```

## Na prática  

Os exemplos a seguir foram retirados e modificados de *Elementos de Máquinas de Shigley* - 10ª Edição, Richard G. Budynas, J. Keith Nisbeth.

> [!TIP]  
> O aplicativo funciona com dois sistemas de unidade
>  
> Métrico :: **N - m - MPa**  
> Imperial :: **lbf - in - ksi**


### **Exemplo - 1** |
Um eixo com 11,5'' de comprimento é suportado por dois mancais localizados a 0,75" (A) e 10,75" (B) a partir da origem (O). Esse eixo possui duas engrenagens, E1 e E2, que estão distantes 2,75" e 8,5", respectivamente, da origem.

Sobre a engrenagem E1, atua uma força $\textbf{F}_1 =(-197j + 540k)$ lbf com posição $\textbf{r}_1 = (2,75i + 6j)$ in, e sobre a engrenagem E2, atua $\textbf{F}_2 =( -885j - 2431k)$ lbf com posição $\textbf{r}_2 = (8,5i + 1,335j)$. 

<img src="https://github.com/jms3471/7J/blob/main/Exemplos/Exemplo_1/eixo_exemplo_1.png" alt="Desenho Esquemático" width="600" height="auto">

**Plotar o momento fletor no plano horizontal $(x - z)$ e vertical (x - y) e o diagrama do torque.**

***

Adição das características do eixo e quantidade de cargas:  

<img src="https://github.com/jms3471/7J/blob/main/Exemplos/Exemplo_1/p1.png" alt="Estática - Tela 1" width="400" height="auto">

Adição das cargas concentradas (somente $F_1$ mostrada):  

<img src="https://github.com/jms3471/7J/blob/main/Exemplos/Exemplo_1/p2.png" alt="Estática - Tela 2" width="300" height="auto">

Resultado após a adição das duas forças:  

<img src="https://github.com/jms3471/7J/blob/main/Exemplos/Exemplo_1/p3.png" alt="Estática - Resultado" width="600" height="auto">  


> [!NOTE]  
> **Na tela final é apresentado:**
>
> - Cartão com as informações de todas as forças adicionadas;
> - Cartão com as reações nos apoios nas direções horizontal e vertical;
> - Cartão com o momento máximo, em valor absoluto, nas direções horizontal e vertical;
> - Gráficos dos momentos fletores e do momento torsor;
> - Cartão contendo um *slider* que possibilita encontrar o momento fletor e torsor em diversos pontos ao longo do eixo.
>

***

### **Exemplo - 2** |

Em um ressalto usinado de eixo, o diâmetro menor ($\textit{d}$) é $28$ mm, o diâmetro maior $(\textit{D})$ é $42$ mm com um raio de adoçamento $(\textit{r})$ de $2,8$ mm. O momento flexor é $142,2$ Nm e o momento estável de torção é $124,3$ Nm. O eixo de aço termo-tratado tem um limite de ruptura de $735$ MPa e um limite de escoamento de $574$ MPa. A meta de confiabilidade é de $0,99$. 

**Determine o coeficiente de segurança do projeto usando o critério de falha por Goodman.**

<img src="https://github.com/jms3471/7J/blob/main/Exemplos/Exemplo_2/eixo_rebaixo.png" alt="Eixo com rebaixo" width="150" height="auto">  


> [!TIP]  
> O aplicativo possui os seguintes critérios de falha
>  
> Fadiga :: **GOODMAN | GERBER | ASME-ELÍPTICO | SODERBERG**  
> Estático :: **LANGER | von MISES | TRESCA**

Dados de entrada para o aplicativo:

| | | |
| :----------- | :--------------: | -------------------------: |
| d = 28e-3    |$\sigma_{esc}$ = 574| $\sigma_{ut}$ = 735      |
| $M_a$ = 142.2 | $M_m$ = 0 | $M_{max}$ = 142.2 |
|$T_a$ = 0 | $T_m$ = 124.3 | $T_{max}$= 124.3|
| $K_{tf}$ = 1.68 | $q_f$ = 0.85 | ( $K_{ff}$ = 1.577)|
| $K_{ts}$= 1.42 | $q_s$ = 0.92 |( $K_{fs}$ = 1.386)|
| $S_e^{'}$ = 367.5| $k_a$ = 0.787 | $k_b$ = 0.870|
| $k_c$ = 1| $k_d$ = 1| $k_e$ = 0.814 |
| | | |

> [!TIP]
>  
> Os campos $T_{max}$ e $M_{max}$ são mostrados apenas quando o critério de *Langer* for selecionado! Consulte a lista de [símbolos](simbolos.md) para entender a nomenclatura utilizada.

Os dados entre parênteses são inferidos pelo programa, enquanto os valores de  $K_{tf}$,  $q_f$,  $K_{ts}$,  $q_s$ são obtidos a partir de tabelas e gráficos correspondentes, assim como os coeficientes de Marin.

<img src="https://github.com/jms3471/7J/blob/main/Exemplos/Exemplo_2/p1.png" alt="Fadiga - Dados e Resultado" width="700" height="auto">  



## Tecnologias Utilizadas
- [Python](https://www.python.org/)  
- [Flet](https://flet.dev/)  
- [Numpy](https://numpy.org/)  
- [Matplotlib](https://matplotlib.org/)  
- [Sympy](https://www.sympy.org/)


## Licença

Este software está licenciado sob a **[GPLv3-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)**. Ao utilizá-lo, você concorda com os termos aplicáveis.

<img src="https://www.gnu.org/graphics/gplv3-or-later.png" alt="Logo GPLv3">
