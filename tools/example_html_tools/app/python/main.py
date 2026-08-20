import json

from datetime import date
import calendar


MESES = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


DIAS = [
    "domingo",
    "segunda",
    "terça",
    "quarta",
    "quinta",
    "sexta",
    "sábado",
]


def main(params):

    ano = int(
        params["ano"]
    )

    mostrar_feriados = bool(
        params["feriados"]
    )


    html = f"""
    <div class="calendar">

        <h2>
            Calendário {ano}
        </h2>
    """


    for mes in range(1, 13):

        html += f"""
        <section class="month">

            <div class="month-title">
                {MESES[mes - 1].capitalize()}
            </div>

            <table>

                <tr>
        """


        for dia in DIAS:

            classe = (
                "domingo"
                if dia == "domingo"
                else ""
            )

            html += (
                f'<th class="{classe}">'
                f'{dia[:3]}'
                f'</th>'
            )


        html += "</tr>"


        calendario = calendar.Calendar(
            firstweekday=6
        )


        for semana in calendario.monthdays2calendar(
            ano,
            mes
        ):

            html += "<tr>"


            for dia, weekday in semana:

                if dia == 0:

                    html += (
                        '<td class="noday">'
                        '&nbsp;'
                        '</td>'
                    )

                    continue


                classes = []


                if weekday == 0:

                    classes.append(
                        "domingo"
                    )


                if mostrar_feriados:

                    if (
                        mes == 1 and
                        dia == 1
                    ):

                        classes.append(
                            "feriado"
                        )


                html += (
                    f'<td class="{" ".join(classes)}">'
                    f'{dia}'
                    f'</td>'
                )


            html += "</tr>"


        html += """
            </table>

        </section>
        """


    html += """
    </div>
    """


    return html