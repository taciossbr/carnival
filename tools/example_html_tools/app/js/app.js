let pyodide = null;


/* =========================================================
   ELEMENTOS
   ========================================================= */

const botao =
    document.getElementById("gerar");

const status =
    document.getElementById("status");

const erro =
    document.getElementById("erro");

const resultado =
    document.getElementById("resultado");


/* =========================================================
   PARÂMETROS
   ========================================================= */

function obterParametros() {

    const params = {

        ano:
            Number(
                document.getElementById(
                    "ano"
                ).value
            ),

        feriados:
            document.getElementById(
                "feriados"
            ).checked

    };

    if (
        !Number.isInteger(
            params.ano
        ) ||
        params.ano < 1900 ||
        params.ano > 2100
    ) {

        throw new Error(
            "Ano inválido."
        );

    }


    return

}

/* =========================================================
   CÓDIGO PYTHON
   ========================================================= */

const PYTHON = `

// #include python/main.py

`;


/* =========================================================
   PYODIDE
   ========================================================= */

async function carregarPyodide() {

    if (pyodide) {
        return pyodide;
    }

    status.textContent =
        "🐍 Carregando Python...";

    pyodide =
        await loadPyodide();

    return pyodide;
}


/* =========================================================
   EXECUTAR
   ========================================================= */

async function executar(params) {

    const py =
        await carregarPyodide();


    status.textContent =
        "🐍 Carregando código Python...";


    // ---------------------------------------------------------
    // Carrega o código da tool.
    //
    // main(params) fica definido aqui.
    // ---------------------------------------------------------

    await py.runPythonAsync(
        PYTHON
    );


    status.textContent =
        "⚙️ Executando...";


    // ---------------------------------------------------------
    // O JS entrega JSON para o Python.
    // ---------------------------------------------------------

    py.globals.set(
        "PARAMS_JSON",
        JSON.stringify(params)
    );


    // ---------------------------------------------------------
    // Executa main() dentro do Python.
    //
    // O próprio Python faz:
    //
    //     json.loads(...)
    //     main(params)
    //
    // ---------------------------------------------------------

    const retorno =
        await py.runPythonAsync(`

_resultado = main(
    json.loads(PARAMS_JSON)
)

_resultado

`);


    try {

        // -----------------------------------------------------
        // PyProxy -> JavaScript
        // -----------------------------------------------------

        if (
            retorno &&
            typeof retorno.toJs === "function"
        ) {

            return retorno.toJs();

        }

        return retorno;

    }

    finally {

        if (
            retorno &&
            typeof retorno.destroy === "function"
        ) {

            retorno.destroy();

        }

    }

}


/* =========================================================
   GERAR
   ========================================================= */

async function gerar() {

    erro.style.display =
        "none";

    erro.textContent =
        "";

    resultado.innerHTML =
        "";

    botao.disabled =
        true;


    try {

        const params =
            obterParametros();

        const html =
            await executar(
                params
            );


        resultado.innerHTML =
            html;


        status.textContent =
            "✓ Gerado.";

    }

    catch (e) {

        console.error(e);


        erro.style.display =
            "block";


        // -----------------------------------------------------
        // Tenta mostrar TODA a informação disponível.
        // -----------------------------------------------------

        let mensagem = "";

        if (e?.message) {
            mensagem += e.message;
        }

        else {
            mensagem += String(e);
        }


        if (e?.stack) {

            mensagem +=
                "\n\n" +
                e.stack;

        }


        erro.textContent =
            "ERRO:\n\n" +
            mensagem;


        status.textContent =
            "❌ Falha.";

    }

    finally {

        botao.disabled =
            false;

    }

}


/* =========================================================
   INICIALIZAÇÃO
   ========================================================= */

document
    .getElementById("ano")
    .value =
    new Date().getFullYear();


botao.addEventListener(
    "click",
    gerar
);