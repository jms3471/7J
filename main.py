# 7J - Software Educacional Economizador de Tempo do Jonathan v.0
# Avaliar e dimensionar eixos de transmissão
# Copyright (C) 2024 JMS.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# AUTOR: JMS
# DATA: 07/06/2024
# LICENÇA: GPL-3.0-or-later
# VERSÃO: 0

from flet import (
    AlertDialog,
    AppView,
    Card,
    Column,
    Container,
    CrossAxisAlignment,
    Dropdown,
    FilledButton,
    FontWeight,
    IconButton,
    Image,
    ImageFit,
    LinearGradient,
    ListView,
    MainAxisAlignment,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    Radio,
    RadioGroup,
    ResponsiveRow,
    ResponsiveRow,
    Row,
    ScrollMode,
    Slider,
    Switch,
    Tab,
    Tabs,
    Text,
    TextAlign,
    TextDecoration,
    TextField,
    TextStyle,
    TextSpan,
    Theme,
    ThemeMode,
    UserControl,
    alignment,
    app,
    colors,
    dropdown,
    icons
)

from flet.matplotlib_chart import MatplotlibChart

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from sympy import Symbol, nsolve, sqrt
from cycler import cycler


# Parâmetros dos gráficos
mpl.use("svg")
mpl.rcParams["figure.dpi"] = 100
mpl.rcParams["font.weight"] = "bold"
mpl.rcParams["font.size"] = 10
mpl.rcParams["axes.prop_cycle"] = cycler(color=["#21918c"])
mpl.rcParams["axes.titlesize"] = 20
mpl.rcParams["axes.labelpad"] = 6
mpl.rcParams["lines.linewidth"] = 3
mpl.rcParams["ytick.left"] = False


PI = np.pi
LISTA_MATERIAIS = {
    # "Material": [Tensão Ruptura (MPA), Tensão Ruptura (ksi), Tensão Escoamento(MPa), Tensão Escoamento(ksi)]
    "SAE 1006 LQ": [300, 43, 170, 24],
    "SAE 1006 LF": [330, 48, 280, 41],
    "SAE 1010 LQ": [320, 47, 180, 26],
    "SAE 1010 LF": [370, 53, 300, 44],
    "SAE 1015 LQ": [340, 50, 190, 27.5],
    "SAE 1015 LF": [390, 56, 320, 47],
    "SAE 1018 LQ": [400, 58, 220, 32],
    "SAE 1018 LF": [440, 64, 370, 54],
    "SAE 1020 LQ": [380, 55, 210, 30],
    "SAE 1020 LF": [470, 68, 390, 57],
    "SAE 1030 LQ": [470, 68, 260, 37.5],
    "SAE 1030 LF": [520, 76, 440, 64],
    "SAE 1035 LQ": [500, 72, 270, 39.5],
    "SAE 1035 LF": [550, 80, 460, 67],
    "SAE 1040 LQ": [520, 76, 290, 42],
    "SAE 1040 LF": [590, 85, 490, 71],
    "SAE 1045 LQ": [570, 82, 310, 45],
    "SAE 1045 LF": [630, 91, 530, 77],
    "SAE 1050 LQ": [620, 90, 340, 49.5],
    "SAE 1050 LF": [690, 90, 580, 84],
    "SAE 1060 LQ": [680, 98, 370, 54],
    "SAE 1080 LQ": [770, 112, 420, 61.5],
    "SAE 1095 LQ": [830, 120, 460, 66],
}



class TextBold(Text):
    def __init__(self, value: str, size=18):
        super().__init__()
        self.value = value
        self.size = size
        self.weight = FontWeight.BOLD


class TextNormal(Text):
    def __init__(self, value: str):
        super().__init__()
        self.value = value
        self.weight = FontWeight.W_400


class CardTitle(UserControl):
    def __init__(self, texto: str):
        super().__init__()
        self.texto = texto

    def build(self):
        return Row(
            [TextBold(self.texto)],
            alignment=MainAxisAlignment.CENTER)


class Units:
    def __init__(self) -> None:
        self.unidade_comprimento = "m"
        self.unidade_force = "N"
        self.unidade_tensao = "MPa"
        self.fator = 1E-2
        self.fator_cs = 1_000_000


class CleanErrorText:
    def limpar(self, *args: TextField):
        for _ in args:
            _.error_text = ""


def Plot(x, momento, unidade_comprimento, unidade_force, title):
    fig, ax = plt.subplots()
    ax.plot(x, momento)
    ax.fill_between(x, momento, alpha=0.2)
    ax.invert_yaxis()
    ax.set_xlim(0, comp_eixo)
    ax.set_xlabel(unidade_comprimento)
    ax.set_ylabel(unidade_force + chr(183) + unidade_comprimento)
    ax.set_title(title)
    ax.set_frame_on(False)
    return fig


def main(page: Page):
    page.theme = Theme(color_scheme_seed="teal")
    page.theme_mode = ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 600
    page.padding = 5
    page.title = "7J"


    TEXTFIELD_HEIGHT = 65
    DIVIDER = Container(height=25)

    GRADIENTE = Container(
    height=10,
    border_radius=5,
    gradient=LinearGradient(
        begin=alignment.center_left,
        end=alignment.center_right,
        colors=["#fdbb2d", "#22c1c3", "#21918c"],
    ),
)

    NOME_MATERIAIS = []
    for _, j in enumerate(LISTA_MATERIAIS):
        NOME_MATERIAIS.append(dropdown.Option(j))

    units = Units()
    clean_error_text = CleanErrorText()


    def inicio(ce, qf, ap1, ap2):
        global comp_eixo, qt_forces, pos_apoio, d, f, r, torsor

        comp_eixo = float(ce)
        qt_forces = int(qf)
        apoio_1 = float(ap1)
        apoio_2 = float(ap2)
        pos_apoio = [apoio_1, apoio_2]

        d = []
        d.append(apoio_1)
        d.append(apoio_2)
        f = np.zeros((qt_forces, 3))
        r = np.zeros((qt_forces, 3))

        torsor = np.zeros(qt_forces)

    def cargas(*args):
        fy = float(args[0])
        fz = float(args[1])
        rx = float(args[2])
        ry = float(args[3])
        rz = float(args[4])
        cont = int(args[5])

        # f[cont,0] = 0.
        f[cont, 1] = fy
        f[cont, 2] = fz
        r[cont, 0] = rx
        r[cont, 1] = ry
        r[cont, 2] = rz
        d.append(r[cont, 0])

    def momento_fletor():
        r[:, 0] -= pos_apoio[0]
        Ma = np.sum(np.cross(r, f), axis=0)
        d_apoio = pos_apoio[1] - pos_apoio[0]

        Bx = 0.0
        By = -Ma[2] / d_apoio
        Bz = Ma[1] / d_apoio

        Ax = 0.0
        Ay = -By
        Az = -Bz
        for i in range(qt_forces):
            Ay -= f[i, 1]
            Az -= f[i, 2]

        A = np.array([[Ax, Ay, Az]])
        B = np.array([[Bx, By, Bz]])

        f_ext = f
        f_ext = np.concatenate((B, f_ext))
        f_ext = np.concatenate((A, f_ext))

        # Discretização do eixo e inicialização das forças e momentos
        n = 1000
        x = np.linspace(0, comp_eixo, num=n)
        Mh, Mv, Mt = np.zeros(n), np.zeros(n), np.zeros(n)
        fy, fz = 0.0, 0.0

        for i in range(qt_forces + 2):
            fz = f_ext[i, 2]
            fy = f_ext[i, 1]

            x_ = (x >= d[i]) * (x - d[i])
            Mh -= fz * x_
            Mv += fy * x_

        for i in range(qt_forces):
            idx_ = np.where(x >= (r[i, 0] + pos_apoio[0]))[0][0]
            Mt[idx_:] += r[i, 1] * f[i, 2] - r[i, 2] * f[i, 1]

        Mh_max = np.max(np.abs(Mh))
        Mv_max = np.max(np.abs(Mv))

        # Correção dos Extremos dos Momentos
        Mh[0], Mh[-1] = 0.0, 0.0
        Mv[0], Mv[-1] = 0.0, 0.0
        Mt[0], Mt[-1] = 0.0, 0.0

        # Momento Horizontal
        fig1 = Plot(x, Mh, units.unidade_comprimento, units.unidade_force, "Momento Fletor - Plano Horizontal (X-Z)")

        # Momento Vertical
        fig2 = Plot(x, Mv, units.unidade_comprimento, units.unidade_force, "Momento Fletor - Plano Vertical (X-Y)" )

        # Momento Torsor
        fig3 = Plot(x, Mt, units.unidade_comprimento, units.unidade_force, "Diagrama do Torque" )


        # Inicialização do slider
        divisions_slider = int(100)
        id0 = int(n / 2)
        mh_texto = TextBold(
            f"{Mh[id0]:.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}")
        mv_texto = TextBold(
            f"{Mv[id0]:.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}")
        mr_texto = TextBold(
            f"{np.sqrt(Mh[id0]**2 + Mv[id0]**2):.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}")
        mt_texto = TextBold(
            f"{Mt[id0]:.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}")

        def mudar_label(e):
            texto.value = (
                f"Posição no eixo ({slider.value:.3f} {units.unidade_comprimento}):")
            id = int((float(str(slider.value)) / x[-1]) * 1000) - 1
            mh_texto.value = (
                f"{Mh[id]:.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}")
            mv_texto.value = (
                f"{Mv[id]:.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}")
            mr_texto.value = f"{np.sqrt(Mh[id]**2 + Mv[id]**2):.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}"
            mt_texto.value = (
                f"{Mt[id]:.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}")
            page.update()

        lv = ListView(
            col={"sm": 4},
            controls=[
                Row(
                    [
                        Text(),
                        TextBold("Fy", 16),
                        TextBold("Fz", 16),
                        TextBold("rx", 16),
                        TextBold("ry", 16),
                        TextBold("rz", 16),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                )
            ],
            spacing=10,
            padding=20,
            divider_thickness=1,
        )

        for i in range(qt_forces):
            lv.controls.append(
                Row(
                    [
                        TextNormal(f"{i+1})"),
                        TextNormal(f"{f_ext[i+2][1]}"),
                        TextNormal(f"{f_ext[i+2][2]}"),
                        TextNormal(f"{r[i,0] + pos_apoio[0]}"),
                        TextNormal(f"{r[i,1]}"),
                        TextNormal(f"{r[i,2]}"),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                )
            )

        texto_forces = ResponsiveRow(
            [
                Column(
                    [
                        TextNormal("Apoio A"),
                        TextBold(f"Ay:  {f_ext[0][1]:.2f} {units.unidade_force}"),
                        TextBold(f"Az:  {f_ext[0][2]:.2f} {units.unidade_force}"),
                    ],
                    col={"xs": 6},
                    alignment=MainAxisAlignment.CENTER,
                ),
                Column(
                    [
                        TextNormal("Apoio B"),
                        TextBold(f"By:  {f_ext[1][1]:.2f} {units.unidade_force}"),
                        TextBold(f"Bz:  {f_ext[1][2]:.2f} {units.unidade_force}"),
                    ],
                    col={"xs": 6},
                    alignment=MainAxisAlignment.CENTER,
                ),
            ],
            spacing=10,
        )

        texto_momento_max = ResponsiveRow(
            [
                Column(
                    [
                        TextNormal("Horizontal"),
                        TextBold(
                            f"{Mh_max:.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}"
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    col={"xs": 6},
                ),
                Column(
                    [
                        TextNormal("Vertical"),
                        TextBold(
                            f"{Mv_max:.2f} {units.unidade_force + chr(183) + units.unidade_comprimento}"
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    col={"xs": 6},
                ),
            ],
            spacing=10,
            alignment=MainAxisAlignment.SPACE_AROUND,
        )

        texto = Text(
            col={"sm": 6},
            value=f"Posição no eixo ({x[id0]:.2f} {units.unidade_comprimento}):",
            weight=FontWeight.BOLD,
            size=18,
        )
        slider = Slider(
            col={"sm": 6},
            active_color="#21918c",
            thumb_color="#22c1c3",
            value=x[-1] / 2,
            min=x[0],
            max=x[-1],
            divisions=divisions_slider,
            on_change=mudar_label,
        )

        texto_momento = ResponsiveRow(
            [
                Column(
                    [
                        TextNormal("Momento Horizontal"),
                        mh_texto,
                        Container(height=20),
                        TextNormal("Momento Vertical"),
                        mv_texto,
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    col={"xs": 6},
                ),
                Column(
                    [
                        TextNormal("Momento Resultante"),
                        mr_texto,
                        Container(height=20),
                        TextNormal("Momento Torsor"),
                        mt_texto,
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    col={"xs": 6},
                ),
            ],
            alignment=MainAxisAlignment.SPACE_EVENLY,
        )

        return Column(
            controls=[
                ResponsiveRow(
                    [
                        Card(
                            content=Container(
                                content=Column(
                                    [
                                        CardTitle(
                                            f"Força(s) Adicionada(s) [{units.unidade_force} - {units.unidade_comprimento}]"
                                        ),
                                        Container(
                                            content=lv,
                                            padding=0,
                                            height=0.15 * page.height,
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_AROUND,
                                ),
                                height=0.25 * page.height,
                                margin=5,
                            ),
                            col={"sm": 6},
                            elevation=3,
                            margin=5,
                        ),
                        Card(
                            content=Container(
                                content=Column(
                                    [
                                        CardTitle("Reações"),
                                        texto_forces,
                                    ],
                                    spacing=10
                                ),
                                height=0.25 * page.height,
                                margin=5,
                            ),
                            col={"sm": 3.5},
                            elevation=3,
                            margin=5,
                        ),
                        Card(
                            content=Container(
                                content=Column(
                                    [
                                        CardTitle("Momento Máximo (Abs)"),
                                        texto_momento_max,
                                    ],
                                    alignment=MainAxisAlignment.SPACE_AROUND,
                                    spacing=10
                                ),
                                height=0.25 * page.height,
                                margin=5,
                            ),
                            elevation=3,
                            col={"sm": 2.5},
                            margin=5,
                        ),
                    ],
                    spacing=10,
                ),
                GRADIENTE,
                Container(
                    content=ResponsiveRow(
                        [
                            MatplotlibChart(fig1, col={"md": 6}),
                            MatplotlibChart(fig2, col={"md": 6}),
                        ]
                    )
                ),
                ResponsiveRow(
                    controls=[
                        MatplotlibChart(fig3, col={"md": 6}, expand=True),
                        Card(
                            col={"md": 6},
                            elevation=3,
                            margin=5,
                            content=Container(
                                height=0.35 * page.height,
                                alignment=alignment.center,
                                margin=10,
                                content=Column(
                                    controls=[
                                        ResponsiveRow(
                                            [texto, slider],
                                            alignment=MainAxisAlignment.SPACE_EVENLY,
                                            vertical_alignment=CrossAxisAlignment.CENTER,
                                        ),
                                        texto_momento,
                                    ],
                                    alignment=MainAxisAlignment.CENTER,
                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                ),
                            ),
                        ),
                    ],
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
        )

    def adicionar(e):
        adicionar_forces.focus()

        if (
            comprimento_eixo.error_text == ""
            and quantidade_forces.error_text == ""
            and apoio_1.error_text == ""
            and apoio_2.error_text == ""
        ):
            inicio(
                comprimento_eixo.value,
                quantidade_forces.value,
                apoio_1.value,
                apoio_2.value,
            )
            remover_forces.disabled = False
            adicionar_forces.disabled = True
            botao_mais.disabled = False
            fy.disabled = False
            fz.disabled = False
            rx.disabled = False
            ry.disabled = False
            rz.disabled = False
            comprimento_eixo.value = ""
            quantidade_forces.value = ""
            apoio_1.value = ""
            apoio_2.value = ""

            numero_force.value = "# 1"
            menus.tabs.pop(0) # type: ignore
            menus.tabs.insert(0, forces_aba) # type: ignore


            page.update()

    def remover(e):
        remover_forces.disabled = True
        adicionar_forces.disabled = False
        page.count = 1  # type: ignore
        botao_mais.disabled = True

        fy.disabled = True
        fz.disabled = True
        rx.disabled = True
        ry.disabled = True
        rz.disabled = True

        fy.value = ""
        fz.value = ""
        rx.value = ""
        ry.value = ""
        rz.value = ""

        menus.tabs.pop(0)  # type: ignore
        menus.tabs.insert(0, dados_iniciais)  # type: ignore


        page.update()

    # Rastreia a quantidade de vezes que o botão foi apertado
    page.count = 1  # type: ignore

    def forces(e):
        botao_mais.focus()
        if (
            fy.error_text == ""
            and fz.error_text == ""
            and rx.error_text == ""
            and ry.error_text == ""
            and rz.error_text == ""
        ):
            try:
                cargas(fy.value, fz.value, rx.value, ry.value, rz.value, page.count - 1)  # type: ignore
                numero_force.value = f"# {page.count+1}"  # type: ignore
                page.count += 1  # type:ignore

                if page.count > qt_forces:  # type:ignore
                    numero_force.value = "#"
                    botao_mais.disabled = True
                    fy.disabled = True
                    fz.disabled = True
                    rx.disabled = True
                    ry.disabled = True
                    rz.disabled = True

                    resultados = Tab(
                        text="Análise Estática",
                        content=Column(
                            controls=[
                                momento_fletor(),
                                Container(height=20),
                                remover_forces,
                            ],
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            scroll=ScrollMode.AUTO,
                        ),
                    )

                    menus.tabs.pop(0)  # type: ignore
                    menus.tabs.insert(0, resultados)  # type: ignore

            except:
                print("Algum erro aconteceu!")


            fy.value = ""
            fz.value = ""
            rx.value = ""
            ry.value = ""
            rz.value = ""

        page.update()

    def dinamica(e):
        btn_verificar.focus()
        page.update()



        if (
            diametro.error_text == "" or None
            and cs.error_text == "" or None
            and ma.error_text == "" or None
            and mm.error_text == "" or None
            and ta.error_text == "" or None
            and tm.error_text == "" or None
            and m_max.error_text == "" or None
            and t_max.error_text == "" or None
            and sigma_e.error_text == "" or None
            and sigma_u.error_text == "" or None
            and ktf.error_text == "" or None
            and qf.error_text == "" or None
            and kts.error_text == "" or None
            and qs.error_text == "" or None
            and limite_fadiga_linha.error_text == "" or None
            and ka.error_text == "" or None
            and kb.error_text == "" or None
            and kc.error_text == "" or None
            and kd.error_text == "" or None
            and ke.error_text == "" or None
        ):

            card_fadiga.visible = True

            x = Symbol("x")

            check = [
                sigma_e.value,
                sigma_u.value,
                ma.value,
                mm.value,
                ta.value,
                tm.value,
                m_max.value,
                t_max.value,
                limite_fadiga.value,
                limite_fadiga_linha.value,
            ]
            for idx, val in enumerate(check):
                if val == "":
                    if idx == 0:
                        sigma_e.value = "0"
                    elif idx == 1:
                        sigma_u.value = "0"
                    elif idx == 2:
                        ma.value = "0"
                    elif idx == 3:
                        mm.value = "0"
                    elif idx == 4:
                        ta.value = "0"
                    elif idx == 5:
                        tm.value = "0"
                    elif idx == 6:
                        m_max.value = "0"
                    elif idx == 7:
                        t_max.value = "0"
                    elif idx == 8:
                        limite_fadiga.value = "1"
                    else:
                        limite_fadiga_linha.value = "1"

            tensao_escoamento = float(str(sigma_e.value)) * units.fator_cs
            tensao_ruptura = float(str(sigma_u.value)) * units.fator_cs

            Kff = float(str(kff.value))
            Kfs = float(str(kfs.value))

            Ma = float(str(ma.value))
            Mm = float(str(mm.value))
            Ta = float(str(ta.value))
            Tm = float(str(tm.value))
            Mmax = float(str(m_max.value))
            Tmax = float(str(t_max.value))


            A = np.sqrt(4 * (Kff * Ma) ** 2 + 3 * (Kfs * Ta) ** 2)
            B = np.sqrt(4 * (Kff * Mm) ** 2 + 3 * (Kfs * Tm) ** 2)

            if escolha_limite_fadiga.value == True:
                try:
                    marin_ka = float(str(ka.value))
                    marin_kc = float(str(kc.value))
                    marin_kd = float(str(kd.value))
                    marin_ke = float(str(ke.value))

                    if escolha_d_.value == True:
                        if kb_radio.value == "1":
                            if units.unidade_comprimento == 'm':
                                mult = 0.592
                                marin_kb = mult * x ** (-0.107) # type: ignore
                            else:
                                mult = 0.879
                                marin_kb = mult *  x ** (-0.107)  # type: ignore


                        elif kb_radio.value == "2":
                            if units.unidade_comprimento == 'm':
                                mult = 0.51
                                marin_kb = mult * x ** (-0.157) # type: ignore
                            else:
                                mult = 0.91
                                marin_kb = mult *  x ** (-0.157)  # type: ignore

                        else:
                            marin_kb = float(str(kb.value))
                    else:
                        marin_kb = float(str(kb.value))
                except:
                    marin_ka = 1.0
                    marin_kb = 1.0
                    marin_kc = 1.0
                    marin_kd = 1.0
                    marin_ke = 1.0

                Se = (
                    marin_ka
                    * marin_kb
                    * marin_kc
                    * marin_kd
                    * marin_ke
                    * float(str(limite_fadiga_linha.value))
                ) * units.fator_cs

            else:
                try:
                    Se = float(str(limite_fadiga.value)) * units.fator_cs
                except:
                    Se = 1



            if escolha_d_.value == False:
                diam = float(str(diametro.value))

                sigma_fm = 32 * Mm / (PI * diam**3)
                sigma_fa = 32 * Ma / (PI * diam**3)
                tau_m = 16 * Tm / (PI * diam**3)
                tau_a = 16 * Ta / (PI * diam**3)
                sigma_m_linha = np.sqrt((Kff * sigma_fm) ** 2 + 3 * (Kfs * tau_m) ** 2)
                sigma_a_linha = np.sqrt((Kff * sigma_fa) ** 2 + 3 * (Kfs * tau_a) ** 2)
                

                if criterio.value == "Goodman":
                    try:
                        CS = (Se * tensao_ruptura / (sigma_a_linha * tensao_ruptura + Se * sigma_m_linha))
                        texto_fadiga.value = f"CS por GOODMAN: {CS:.3f}"
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "Gerber":
                    try:
                        CS = (PI * Se * diam**3 / (8 * A * (1 + (1 + (2 * B * Se / (A * tensao_ruptura)) ** 2) ** 0.5)))
                        texto_fadiga.value = f"CS por GERBER: {CS:.3f}"
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "ASME Elíptico":
                    try:
                        CS = (PI * diam**3 / (16 * ( 4 * (Kff * Ma / Se) ** 2 + 
                                3 * (Kfs * Ta / Se) ** 2 + 4 * (Kff * Mm / tensao_escoamento) ** 2 + 3 * (Kfs * Tm / tensao_escoamento) ** 2)** 0.5))
                        texto_fadiga.value = f"CS por ASME ELÍPTICO: {CS:.3f}"
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "Soderberg":
                    try:
                        CS = (PI* diam**3 / (16 * (((4 * (Kff * Ma) ** 2 + 3 * (Kfs * Ta) ** 2) ** 0.5) / Se
                                    + ((4 * (Kff * Mm) ** 2 + 3 * (Kfs * Tm) ** 2)** 0.5) / tensao_escoamento)))
                        texto_fadiga.value = f"CS por SODERBERG: {CS:.3f}"
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "Langer (Estático)":
                    try:
                        tensao_max = np.sqrt(
                            (32 * Kff * Mmax / (PI * diam**3)) ** 2
                            + 3 * (16 * Kfs * Tmax / (PI * diam**3)) ** 2)
                        CS = tensao_escoamento / tensao_max
                        texto_fadiga.value = f"CS por Langer: {CS:.3f}"
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "von Mises (Estático)":
                    try:
                        sigma_max = 32*Kff*(Ma + Mm)/ (PI * diam**3)
                        tau_max = 16*Kfs*(Ta + Tm) / (PI * diam**3)
                        sigma_linha = (sigma_max**2 + 3*tau_max**2) ** (1/2)
                        CS = tensao_escoamento / sigma_linha
                        texto_fadiga.value = f"CS por von Mises: {CS:.3f}"
                    except:
                        texto_fadiga.value = "ERRO!"
                
                elif criterio.value == "Tresca (Estático)":
                    try:
                        tau_max = ((16*Kff*(Ma+Mm)/(PI * diam**3))**2 + (16*Kfs*(Ta + Tm) / (PI * diam**3))**2) ** 0.5
                        CS = tensao_escoamento / (2*tau_max)
                        texto_fadiga.value = f"CS por Tresca: {CS:.3f}"
                    except:
                        texto_fadiga.value = "ERRO!"
                
                else:
                    texto_fadiga.value = "ERRO!"
            
            else:
                CS = float(str(cs.value))
                if criterio.value == "Goodman":
                    try:
                        expression = (
                            16 * CS * (
                                ((4 * (Kff * Ma) ** 2 + 3 * (Kfs * Ta) ** 2) ** 0.5) / Se
                                + ((4 * (Kff * Mm) ** 2 + 3 * (Kfs * Tm) ** 2) ** 0.5 / tensao_ruptura)) / PI) ** (1.0 / 3)
                        texto_fadiga.value = f"Diâmetro por GOODMAN: {nsolve(x - expression, 0.5 ):.3E} {units.unidade_comprimento}" # type: ignore
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "Gerber":
                    try:
                        expression = (8 * CS * A * (1 + (1 + (2 * B * Se / (A * tensao_ruptura)) ** 2) ** 0.5) / (PI * Se)) ** (1.0 / 3)
                        texto_fadiga.value = f"Diâmetro por GERBER: {nsolve(x - expression, 0.5):.3E} {units.unidade_comprimento}" # type: ignore
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "ASME Elíptico":
                    try:
                        expression = ((16*CS/PI) * ((4*(Kff*Ma/Se)**2 + 4*(Kff*Mm/tensao_escoamento)**2 + 3*(Kfs*Ta/Se)**2 + 3*(Kfs*Tm/tensao_escoamento)**2 ) ** 0.5))**(1./3)
                        texto_fadiga.value = f"Diâmetro por ASME ELÍPTICO: {nsolve(x - expression, 0.5 ):.3E} {units.unidade_comprimento}" # type: ignore
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "Soderberg":
                    try:
                        expression = x - (16* CS * ((4 * (Kff * Ma) ** 2 + 3 * (Kfs * Ta) ** 2) ** 0.5 / Se
                                + (4 * (Kff * Mm) ** 2 + 3 * (Kfs * Tm) ** 2) ** 0.5 / tensao_escoamento) / PI) ** (1.0 / 3)
                        texto_fadiga.value = f"Diâmetro por SODERBERG: {nsolve(expression, 0.5):.3E} {units.unidade_comprimento}" # type: ignore
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "Langer (Estático)":
                    try:
                        tensao_max = sqrt((32 * Kff * Mmax / (PI * x**3)) ** 2 + 3 * (16 * Kfs * Tmax / (PI * x**3)) ** 2)  # type: ignore
                        expression = tensao_max - tensao_escoamento / (CS * units.fator_cs)  # type: ignore
                        dLanger = nsolve(expression, 0.5)
                        texto_fadiga.value = f"Diâmetro por Langer: {units.fator*dLanger:.3E} {units.unidade_comprimento}" # type: ignore
                    except:
                        texto_fadiga.value = "ERRO!"
                
                elif criterio.value == "von Mises (Estático)":
                    try:
                        sigma_max = 32*Kff*(Ma + Mm)/ (PI * x**3) #type: ignore
                        tau_max = 16*Kfs*(Ta + Tm) / (PI * x**3) #type: ignore
                        sigma_linha = (sigma_max**2 + 3*tau_max**2) ** (1/2)
                        expression = -sigma_linha * (CS * units.fator_cs) + tensao_escoamento
                        dMises = nsolve(expression, 0.5)
                        texto_fadiga.value = f"Diâmetro por von Mises: {units.fator*dMises:.3E} {units.unidade_comprimento}" # type: ignore
                    except:
                        texto_fadiga.value = "ERRO!"

                elif criterio.value == "Tresca (Estático)":
                    try:
                        tau_max = ((16*Kff*(Ma+Mm)/(PI * x**3))**2 + (16*Kfs*(Ta + Tm) / (PI * x**3))**2) ** 0.5 # type: ignore
                        expression = (2*tau_max) * (CS * units.fator_cs) - tensao_escoamento 
                        dTresca = nsolve(expression, 0.5)
                        texto_fadiga.value = f"Diâmetro por Tresca: {units.fator*dTresca:.3E} {units.unidade_comprimento}" # type: ignore
                    except:
                        texto_fadiga.value = "ERRO!"

                else:
                    texto_fadiga.value = "ERRO!"

        page.update()

    def escolha_d(e):
        card_fadiga.visible = False
        escolha_cs_.value = not escolha_cs_.value

        if escolha_d_.value == False:
            clean_error_text.limpar(diametro)
            cs.visible = False
            diametro.visible = True
            op1.disabled = True
            op2.disabled = True
            kb_radio.value = "3"
            kb.disabled = False
        else:
            clean_error_text.limpar(cs)
            diametro.visible = False
            cs.visible = True
            op1.disabled = False
            op2.disabled = False

        page.update()

    def escolha_cs(e):
        card_fadiga.visible = False
        escolha_d_.value = not escolha_d_.value

        if escolha_d_.value == False:
            clean_error_text.limpar(cs)
            cs.visible = False
            diametro.visible = True
            op1.disabled = True
            op2.disabled = True
            kb_radio.value = "3"
            kb.disabled = False
        else:
            clean_error_text.limpar(diametro)
            diametro.visible = False
            cs.visible = True
            op1.disabled = False
            op2.disabled = False

        page.update()

    def escolha_se(e):
        if escolha_limite_fadiga.value == False:
            clean_error_text.limpar(limite_fadiga_linha, ka, kb, kc, kd, ke)
            limite_fadiga.visible = True
            limite_fadiga_linha.visible = False
            kb_label.visible = False
            ka.visible = False
            kb.visible = False
            kb_radio.visible = False
            kc.visible = False
            kd.visible = False
            ke.visible = False
            container_fadiga_linha.visible = False
        else:
            clean_error_text.limpar(limite_fadiga)
            limite_fadiga.visible = False
            limite_fadiga_linha.visible = True
            kb_label.visible = True
            ka.visible = True
            kb.visible = True
            kb_radio.visible = True
            kc.visible = True
            kd.visible = True
            ke.visible = True
            container_fadiga_linha.visible = True

        page.update()

    def escolha_kb(e):
        if e.control.value == "1":
            kb.disabled = True
        elif e.control.value == "2":
            kb.disabled = True
        else:
            kb.disabled = False

        page.update()

    def escolha_criterio(e):
        card_fadiga.visible = False

        ma.visible = True
        mm.visible = True
        ta.visible = True
        tm.visible = True
        m_max.visible = False
        t_max.visible = False
        sigma_u.visible = True
        sigma_e.visible = True
        material.visible = True
        container_limite_fadiga.visible = True
        container_material.visible = True

        if criterio.value == "Langer (Estático)":
            ma.visible = False
            mm.visible = False
            ta.visible = False
            tm.visible = False
            sigma_u.visible = False
            sigma_e.visible = True
            m_max.visible = True
            t_max.visible = True
            container_limite_fadiga.visible = False

        page.update()


    def verifica_se_zero(e):
        try:
            verifica_numero(e)
            if float(e.control.value) == 0.:
                raise Exception
        except:
            e.control.error_text = "Valor digitado inválido! Tente novamente."
        
        page.update()
            

    def verifica_unidade(e):
        string = e.control.value

        if string != "":
            try:
                converte = float(string)
                if converte > 1.0 or converte < 0.0:
                    e.control.error_text = "O valor precisa estar entre 0 e 1"
                else:
                    e.control.error_text = ""
            except:
                e.control.error_text = "Valor digitado inválido! Tente novamente."

        page.update()

    def verifica_numero(e):
        string = e.control.value

        if string != "":
            try:
                _ = float(string)
                e.control.error_text = ""
            except:
                e.control.error_text = "Valor digitado inválido! Tente novamente."

        page.update()

    def verifica_comprimento_eixo(e):
        string = e.control.value
        e.control.error_text = ""

        if string != "":
            try:
                converte = float(string)
                if converte <= 0.0:
                    e.control.error_text = (
                        "O comprimento do eixo precisa ser maior que zero!"
                    )
            except:
                e.control.error_text = "Valor digitado inválido! Tente novamente."

        page.update()

    def verifica_posicao_apoio_1(e):
        string = e.control.value
        e.control.error_text = ""

        try:
            tmp_ce = float(str(comprimento_eixo.value))
            if string != "":
                try:
                    posicao = float(string)
                    if posicao < 0.0:
                        e.control.error_text = "Valor precisa ser positivo!"
                    else:
                        if posicao > tmp_ce:
                            e.control.error_text = (
                                f"Valor deve estar entre 0 e {tmp_ce:.2f} {units.unidade_comprimento}."
                            )
                        elif posicao == tmp_ce:
                            e.control.error_text = (
                                f"Valor deve ser menor que {tmp_ce:.2f} {units.unidade_comprimento}."
                            )
                except:
                    e.control.error_text = "Valor digitado inválido!"

        except:
            e.control.error_text = "Precisa adicionar o comprimento do eixo!"

        page.update()

    def verifica_posicao_apoio_2(e):
        string = e.control.value
        e.control.error_text = ""

        try:
            tmp_ce = float(str(comprimento_eixo.value))
            tmp_p1 = float(str(apoio_1.value))
            if string != "":
                try:
                    posicao = float(string)
                    if posicao <= 0.0:
                        e.control.error_text = "Valor precisa ser maior que zero!"
                    else:
                        if posicao > tmp_ce:
                            e.control.error_text = (
                                f"Valor deve estar entre 0 e {tmp_ce:.2f} {units.unidade_comprimento}."
                            )
                        elif posicao <= tmp_p1:
                            e.control.error_text = (
                                f"Valor deve ser maior que {tmp_p1:.2f} {units.unidade_comprimento}."
                            )
                except:
                    e.control.error_text = "Valor digitado inválido!"

        except:
            e.control.error_text = (
                "Precisa adicionar o comprimento \ndo eixo e/ou o valor da posição 1!"
            )

        page.update()

    def verifica_numero_inteiro(e):
        string = e.control.value
        try:
            converte = int(string)
            if converte <= 0:
                raise ValueError
            e.control.error_text = ""
        except:
            e.control.error_text = "Valor digitado inválido! Tente novamente."

        page.update()

    def verifica_numero_rx(e):
        string = e.control.value
        e.control.error_text = ""

        if string != "":
            try:
                rx = float(string)
                if rx < 0.0:
                    e.control.error_text = "Valor precisa ser maior ou igual a zero!"
                elif rx > comp_eixo:
                    e.control.error_text = (
                        f"Valor deve estar entre 0 e {comp_eixo:.2f} {units.unidade_comprimento}."
                    )
            except:
                e.control.error_text = "Valor digitado inválido!"

        page.update()

    def escolha_material(e):
        if material_switch.value == True:
            sigma_e.disabled = False
            sigma_u.disabled = False
            material.disabled = True
        else:
            sigma_e.disabled = True
            sigma_u.disabled = True
            material.disabled = False

            
        sigma_e.error_text = ""
        page.update()

    def mudar_material(e):
        if unidades_radio.value == "SI":
            sigma_u.value = str(LISTA_MATERIAIS.get(e.control.value)[0]) # type: ignore
            sigma_e.value = str(LISTA_MATERIAIS.get(e.control.value)[2]) # type: ignore
        else:
            sigma_u.value = str(LISTA_MATERIAIS.get(e.control.value)[1]) # type: ignore
            sigma_e.value = str(LISTA_MATERIAIS.get(e.control.value)[3]) # type: ignore
        page.update()

    def on_focus(e):
        e.control.error_text = ""
        page.update()

    def estatico_torcao(e):
        if kts_switch.value == True:
            kts.visible = True
            qs.visible = True
            kfs.disabled = True
        else:
            clean_error_text.limpar(kts, qs)
            kts.visible = False
            qs.visible = False
            kfs.disabled = False
            kfs.value = ""

        page.update()

    def kfs_value(e):
        verifica_numero(e)
        try:
            kfs.value = str(1.0 + float(str(qs.value)) * (float(str(kts.value)) - 1.0))[:5]
        except:
            kfs.value = ""

        page.update()

    def estatico_flexao(e):
        if ktf_switch.value == True:
            ktf.visible = True
            qf.visible = True
            kff.disabled = True
        else:
            clean_error_text.limpar(ktf, qf)
            ktf.visible = False
            qf.visible = False
            kff.disabled = False
            kff.value = ""

        page.update()

    def kff_value(e):
        verifica_numero(e)
        try:
            kff.value = str(1.0 + float(str(qf.value)) * (float(str(ktf.value)) - 1.0))[:5]
        except:
            kff.value = ""

        page.update()

    def unidade(e):
        if e.control.value != "SI":
            units.unidade_force = "lbf"
            units.unidade_comprimento = "in"
            units.unidade_tensao = "ksi"
            units.fator = 1E-1
            units.fator_cs = 1_000
        else:
            units.unidade_force = "N"
            units.unidade_comprimento = "m"
            units.unidade_tensao = "MPa"
            units.fator = 1E-2
            units.fator_cs = 1_000_000

        for i in unidade_medida:
            i.suffix_text = units.unidade_comprimento
        for j in unidade_momento:
            j.suffix_text = units.unidade_force + chr(183) + units.unidade_comprimento
        for k in unidade_limite:
            k.suffix_text = units.unidade_tensao

        fy.suffix_text = units.unidade_force
        fz.suffix_text = units.unidade_force

        page.update()

    def open_dlg(e):
        page.dialog = dlg
        dlg.open = True
        page.update()

    unidades_radio = RadioGroup(
        content=Column(
            [
                Radio(value="SI", label="N - m - MPa"),
                Radio(value="NSI", label="lbf - in - ksi"),
            ]),
        value="SI",
        on_change=unidade,
    )

    pop_menu = PopupMenuButton(
        items=[
            PopupMenuItem(content=unidades_radio),
            PopupMenuItem(),
            PopupMenuItem(icon=icons.INFO_OUTLINE,text="Sobre", on_click=open_dlg)
        ],
        tooltip="Menu",
    )

    dlg = AlertDialog(
    title=Text("SETe Jota v.0", size=20, weight=FontWeight.W_500, text_align=TextAlign.CENTER),
    content=Column([Text("Software Educacional Economizador de Tempo do Jonathan", size=16, weight=FontWeight.W_600, expand=2),
                    Text("Criado por JMS sob licença GPLv3", size=15, weight=FontWeight.W_400, expand=1 ),
                    Text("Disponível em: ", spans=[TextSpan("github.com/jms3471/7J", TextStyle(weight=FontWeight.W_600, color=colors.TEAL_800, decoration=TextDecoration.UNDERLINE, decoration_color=colors.TEAL_800), url="https://github.com/jms3471/7J")], size=15, expand=1)],
                    height=120),
    icon=Image(src='icon.png', fit=ImageFit.FIT_HEIGHT, height=50)
    )

    # Dados Análise Estática
    comprimento_eixo = TextField(
        label="Comprimento do Eixo",
        suffix_text=units.unidade_comprimento,
        max_length=6,
        on_blur=verifica_comprimento_eixo,
        on_focus=on_focus,
        dense=True,
        height=TEXTFIELD_HEIGHT,
    )
    quantidade_forces = TextField(
        label="Quantidade de Forças",
        max_length=2,
        on_blur=verifica_numero_inteiro,
        on_focus=on_focus,
        dense=True,
        height=TEXTFIELD_HEIGHT,
    )
    apoio_1 = TextField(
        label="Posição do apoio 1",
        suffix_text=units.unidade_comprimento,
        max_length=6,
        on_blur=verifica_posicao_apoio_1,
        on_focus=on_focus,
        dense=True,
        height=TEXTFIELD_HEIGHT,
    )
    apoio_2 = TextField(
        label="Posição do apoio 2",
        suffix_text=units.unidade_comprimento,
        max_length=6,
        on_blur=verifica_posicao_apoio_2,
        on_focus=on_focus,
        dense=True,
        height=TEXTFIELD_HEIGHT,
    )
    adicionar_forces = FilledButton(text="Adicionar Dados", on_click=adicionar)
    remover_forces = IconButton(
        icon=icons.DELETE_FOREVER,
        disabled=False,
        on_click=remover,
        icon_color="red800",
        icon_size=35,
        tooltip="Remove os dados (estáticos) e volta para o início",
    )

    # Adição de cargas
    numero_force = Text(value="# 1", color="#006D5B", size=30, weight=FontWeight.BOLD)
    fy = TextField(
        label="Fy",
        disabled=True,
        max_length=9,
        suffix_text=units.unidade_force,
        on_blur=verifica_numero,
        on_focus=on_focus,
        dense=True,
        height=TEXTFIELD_HEIGHT,
    )
    fz = TextField(
        label="Fz",
        disabled=True,
        max_length=9,
        suffix_text=units.unidade_force,
        on_blur=verifica_numero,
        on_focus=on_focus,
        dense=True,
        height=TEXTFIELD_HEIGHT,
    )
    rx = TextField(
        label="rx",
        disabled=True,
        max_length=6,
        suffix_text=units.unidade_comprimento,
        on_blur=verifica_numero_rx,
        on_focus=on_focus,
        dense=True,
        height=TEXTFIELD_HEIGHT,
    )
    ry = TextField(
        label="ry",
        disabled=True,
        max_length=6,
        suffix_text=units.unidade_comprimento,
        on_blur=verifica_numero,
        on_focus=on_focus,
        dense=True,
        height=TEXTFIELD_HEIGHT,
    )
    rz = TextField(
        label="rz",
        disabled=True,
        max_length=6,
        suffix_text=units.unidade_comprimento,
        on_blur=verifica_numero,
        on_focus=on_focus,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    botao_mais = IconButton(
        icon=icons.ADD_CIRCLE_OUTLINE,
        disabled=True,
        on_click=forces,
        icon_color="#006D5B",
        icon_size=50,
        tooltip="Adicionar Força",
    )

    # Análise de Fadiga
    escolha_d_ = Switch(
        col={"sm": 6}, label="Encontrar Diâmetro", value=True, on_change=escolha_d
    )
    escolha_cs_ = Switch(
        col={"sm": 6}, label="Encontrar CS", value=False, on_change=escolha_cs
    )
    cs = TextField(
        col={"sm": 6},
        label="CS",
        hint_text="Coeficiente de segurança",
        max_length=5,
        on_blur=verifica_se_zero,
        on_focus=on_focus,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    criterio = Dropdown(
        col={"sm": 6},
        label="Critério",
        value="Goodman",
        on_change=escolha_criterio,
        options=[
            dropdown.Option("Goodman"),
            dropdown.Option("Gerber"),
            dropdown.Option("ASME Elíptico"),
            dropdown.Option("Soderberg"),
            dropdown.Option("Langer (Estático)"),
            dropdown.Option("von Mises (Estático)"),
            dropdown.Option("Tresca (Estático)"),
        ],
        height=0.9 * TEXTFIELD_HEIGHT,
        text_size=14,
        text_style=TextStyle(weight=FontWeight.W_600),
        dense=True,
    )
    diametro = TextField(
        col={"sm": 6},
        label="Diâmetro do Eixo",
        suffix_text=units.unidade_comprimento,
        visible=False,
        max_length=7,
        on_blur=verifica_se_zero,
        on_focus=on_focus,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )

    material_switch = Switch(
        label="Usar material personalizado", value=False, on_change=escolha_material,
        
    )
    material = Dropdown(
        label="Material",
        options=NOME_MATERIAIS,
        disabled=False,
        on_change=mudar_material,
        height=0.9 * TEXTFIELD_HEIGHT,
        text_size=14,
        text_style=TextStyle(weight=FontWeight.W_600),
        dense=True,
    )

    ma = TextField(
        col={"sm": 6},
        label="Ma",
        hint_text="Momento fletor alternado",
        suffix_text=units.unidade_force + chr(183) + units.unidade_comprimento,
        max_length=8,
        on_focus=on_focus,
        on_blur=verifica_numero,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    mm = TextField(
        col={"sm": 6},
        label="Mm",
        hint_text="Momento fletor médio",
        suffix_text=units.unidade_force + chr(183) + units.unidade_comprimento,
        max_length=8,
        on_focus=on_focus,
        on_blur=verifica_numero,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    m_max = TextField(
        col={"sm": 6},
        label="Mmáx",
        hint_text="Momento fletor máximo",
        suffix_text=units.unidade_force + chr(183) + units.unidade_comprimento,
        visible=False,
        max_length=8,
        on_focus=on_focus,
        on_blur=verifica_numero,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    ta = TextField(
        col={"sm": 6},
        label="Ta",
        hint_text="Momento torsor alternado",
        suffix_text=units.unidade_force + chr(183) + units.unidade_comprimento,
        max_length=8,
        on_focus=on_focus,
        on_blur=verifica_numero,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    tm = TextField(
        col={"sm": 6},
        label="Tm",
        hint_text="Momento torsor médio",
        suffix_text=units.unidade_force + chr(183) + units.unidade_comprimento,
        max_length=8,
        on_focus=on_focus,
        on_blur=verifica_numero,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    t_max = TextField(
        col={"sm": 6},
        label="Tmáx",
        hint_text="Momento torsor máximo",
        suffix_text=units.unidade_force + chr(183) + units.unidade_comprimento,
        visible=False,
        max_length=8,
        on_focus=on_focus,
        on_blur=verifica_numero,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )

    sigma_e = TextField(
        label=chr(963) + "e",
        hint_text="Tensão de escoamento",
        suffix_text=units.unidade_tensao,
        disabled=True,
        # visible=False,
        max_length=5,
        on_focus=on_focus,
        on_blur=verifica_se_zero,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    sigma_u = TextField(
        label=chr(963) + "u",
        hint_text="Tensão de ruptura",
        suffix_text=units.unidade_tensao,
        disabled=True,
        max_length=5,
        on_focus=on_focus,
        on_blur=verifica_se_zero,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    container_material = Container(
        content=Column([material_switch, material, sigma_e, sigma_u])
    )
    escolha_limite_fadiga = Switch(
        label="Encontrar Se", 
        value=True, 
        on_change=escolha_se,
    )
    limite_fadiga = TextField(
        label="Se",
        suffix_text=units.unidade_tensao,
        hint_text="Limite de Fadiga",
        visible=False,
        max_length=5,
        on_focus=on_focus,
        on_blur=verifica_se_zero,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    limite_fadiga_linha = TextField(
        col={"sm": 6},
        label="S'ₑ",
        hint_text="Limite de Fadiga do corpo de prova",
        suffix_text=units.unidade_tensao,
        max_length=5,
        on_focus=on_focus,
        on_blur=verifica_se_zero,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    ka = TextField(
        col={"sm": 6},
        label="ka",
        hint_text="Fator de acabamento superficial",
        on_blur=verifica_unidade,
        max_length=5,
        on_focus=on_focus,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    kb_label = Text(value="Fator de Tamanho", weight=FontWeight.W_600)
    kb = TextField(
        col={"sm": 6},
        label="kb",
        hint_text="Fator de tamanho",
        on_blur=verifica_unidade,
        on_focus=on_focus,
        disabled=True,
        max_length=5,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    op1 = Radio(value="1", label='Diâmetro até 51mm (2")')
    op2 = Radio(value="2", label='Diâmetro maior que 51mm (2")')
    op3 = Radio(value="3", label="Inserir kb")
    kb_radio = RadioGroup(
        value="1",
        on_change=escolha_kb,
        content=Column(
            [
                op1,
                op2,
                op3,
            ]
        ),
    )
    kb_ = Column([kb_radio, kb])
    kc = TextField(
        col={"sm": 6},
        label="kc",
        hint_text="Fator de carregamento",
        on_blur=verifica_unidade,
        max_length=5,
        on_focus=on_focus,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    kd = TextField(
        col={"sm": 6},
        label="kd",
        hint_text="Fator de temperatura",
        on_blur=verifica_unidade,
        max_length=5,
        on_focus=on_focus,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    ke = TextField(
        col={"sm": 6},
        label="ke",
        hint_text="Fator de confiabilidade",
        on_blur=verifica_unidade,
        max_length=5,
        on_focus=on_focus,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )

    container_fadiga_linha = Column(
        [
            ResponsiveRow([limite_fadiga_linha, ka], spacing=30),
            ResponsiveRow(
                [
                    Container(
                        col={"sm": 6},
                        content=Column(
                            [Row(height=0.009 * page.height), kb_label, kb_]
                        ),
                        height=0.42 * page.height,
                    ),
                    Container(
                        col={"sm": 6},
                        content=Column([kc, kd, ke]),
                        height=0.42 * page.height,
                    ),
                ],
                spacing=30,
            ),
        ]
    )

    container_limite_fadiga = Container(
        padding=10,
        content=Column(
            [escolha_limite_fadiga, limite_fadiga, container_fadiga_linha],
        ),
    )
    kff = TextField(
        label="Kff",
        hint_text="Fator de concentração de tensão em fadiga para cargas em flexão",
        on_blur=verifica_numero,
        max_length=5,
        on_focus=on_focus,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    kfs = TextField(
        label="Kfs",
        hint_text="Fator de concentração de tensão em fadiga para cargas em torção",
        on_blur=verifica_numero,
        on_focus=on_focus,
        max_length=5,
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )

    ktf_switch = Switch(label="Ktf", value=False, on_change=estatico_flexao)
    ktf = TextField(
        label="Ktf",
        hint_text="Fator de concentração de tensão estático para flexão",
        visible=False,
        max_length=5,
        on_change=kff_value,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    qf = TextField(
        label="qf",
        hint_text="Fator de sensibilidade ao entalhe para flexão",
        visible=False,
        max_length=5,
        on_change=kff_value,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    container_ktf = Container(
        col={"sm": 6}, content=Column(controls=[ktf_switch, ktf, qf, kff])
    )

    kts_switch = Switch(label="Kts", value=False, on_change=estatico_torcao)
    kts = TextField(
        label="Kts",
        hint_text="Fator de concentração de tensão estático para torção",
        visible=False,
        max_length=5,
        on_change=kfs_value,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    qs = TextField(
        label="qs",
        hint_text="Fator de sensibilidade ao entalhe para torção",
        visible=False,
        max_length=5,
        on_change=kfs_value,
        error_text="",
        height=TEXTFIELD_HEIGHT,
        dense=True,
    )
    container_kts = Container(
        col={"sm": 6}, content=Column(controls=[kts_switch, kts, qs, kfs])
    )

    texto_fadiga = Text(size=20, weight=FontWeight.BOLD)

    btn_verificar = FilledButton(text="Verificar", on_click=dinamica)

    card_fadiga = ResponsiveRow(
        [
            Card(
                content=Container(
                    content=Column(
                        [texto_fadiga], alignment=MainAxisAlignment.SPACE_AROUND
                    ),
                    height=0.1 * page.height,
                    alignment=alignment.center,
                    margin=10,
                ),
                elevation=3,
                margin=5,
            )
        ],
        alignment=MainAxisAlignment.CENTER,
        visible=False,
    )

    unidade_medida = [comprimento_eixo, apoio_1, apoio_2, rx, ry, rz, diametro]
    unidade_momento = [ma, mm, m_max, ta, tm, t_max]
    unidade_limite = [sigma_e, sigma_u, limite_fadiga, limite_fadiga_linha]

    # Abas
    dados_iniciais = Tab(
        text="Análise Estática",
        content=Container(
            alignment=alignment.center,
            padding=10,
            bgcolor=colors.WHITE10,
            content=Column(
                spacing=20,
                scroll=ScrollMode.AUTO,
                alignment=MainAxisAlignment.SPACE_AROUND,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Row([pop_menu], alignment=MainAxisAlignment.END),
                    Row(
                        [
                            Image(src=f"eixos.png", fit=ImageFit.FIT_WIDTH, width=140),
                            Text(value="Eixo x é a direção axial\ndo elemento"),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    DIVIDER,
                    comprimento_eixo,
                    DIVIDER,
                    quantidade_forces,
                    DIVIDER,
                    apoio_1,
                    DIVIDER,
                    apoio_2,
                    DIVIDER,
                    Row(
                        controls=[adicionar_forces], alignment=MainAxisAlignment.CENTER
                    ),
                ],
            ),
        ),
    )

    forces_aba = Tab(
        text="Análise Estática",
        content=Container(
            alignment=alignment.center,
            padding=10,
            bgcolor=colors.WHITE10,
            content=Column(
                [
                    numero_force,
                    fy,
                    DIVIDER,
                    fz,
                    DIVIDER,
                    rx,
                    DIVIDER,
                    ry,
                    DIVIDER,
                    rz,
                    Row(
                        [botao_mais, remover_forces],
                        alignment=MainAxisAlignment.SPACE_EVENLY,
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_AROUND,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                scroll=ScrollMode.AUTO,
                spacing=20,
            ),
        ),
    )

    menus = Tabs(
        tabs=[
            Tab(
                text="Análise de Fadiga",
                # icon=icons.SETTINGS,
                content=Container(
                    margin=5,
                    alignment=alignment.center,
                    padding=5,
                    content=Column(
                        [
                            ResponsiveRow([Column([escolha_d_, escolha_cs_,], col={"sm": 6})],),
                            Row(),
                            ResponsiveRow(
                                [diametro, cs, criterio, ma, mm, ta, tm, m_max, t_max],
                                spacing=30,
                            ),
                            container_material,
                            ResponsiveRow([container_ktf, container_kts], spacing=30),
                            container_limite_fadiga,
                            card_fadiga,
                            GRADIENTE,
                            Row([btn_verificar], alignment=MainAxisAlignment.CENTER),
                        ],
                        spacing=20,
                        expand=3,
                        scroll=ScrollMode.AUTO,
                    ),
                ),
            ),
        ],
        expand=1,
    )

    menus.tabs.insert(0, dados_iniciais)  # type: ignore
    menus.selected_index = 0

    page.add(menus)


if __name__ == '__main__':
    app(target=main, assets_dir="assets")