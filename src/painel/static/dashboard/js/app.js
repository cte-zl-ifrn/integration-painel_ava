export default {
    compilerOptions: {
        delimiters: ["[[", "]]"],
    },
    data() {
        return {
            semestres: [],
            situacoes: [
                { label: "✳️ Diários em andamento", id: "inprogress" },
                { label: "🗓️ Diários a iniciar", id: "future" },
                { label: "📕 Encerrados pelo professor", id: "past" },
                { label: "⭐ Meus diários favoritos", id: "favourites" },
                { label: "♾️ Todos os diários (lento)", id: "allincludinghidden" },
            ],
            visualizacoes: [
                { label: "Ver como linhas", id: "list" },
                { label: "Ver como cartões", id: "card" },
            ],
            disciplinas: [],
            cursos: [],
            ambientes: [],
            coordenacoes: [],
            praticas: [],
            diarios: [],
            salas: [],
            reutilizaveis: [],
            has_error: false,
            is_filtering: true,
            activeParagraph: null,
            q: localStorage.q || "",
            situacao: localStorage.situacao || "inprogress",
            semestre: localStorage.getItem('semestre') || "",
            disciplina: localStorage.disciplina || "",
            curso: localStorage.curso || "",
            ambiente: localStorage.ambiente || "",
            contentClosed: localStorage.contentClosed || "true",
            screenWidth: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
            isPopupOpen: false,
            isIconUp: false,            
        };
    },
    
    mounted() {
        if (localStorage.contentClosed == "true") {
            $(".filter-wrapper").addClass("closed");
        }
        $(document).ready(() => {
            this.customizeAmbiente();
        });

        this.filterCards();
        $("#app").css("display", "block");
        $("#pre-loading").css("display", "none");
        this.popup();

        // Adiciona um ouvinte de evento para verificar a largura da tela quando a janela é redimensionada
        window.addEventListener("resize", this.handleResize);


    },
    updated() {
        $("#semestre").select2("val", localStorage.getItem('semestre'));
        $("#disciplina").select2("val", localStorage.getItem('disciplina'));
        $("#curso").select2("val", localStorage.getItem('curso'));
        $("#ambiente").select2("val", localStorage.getItem('ambiente'));
    },

    methods: {
        getSemestreName(semestreId) {
            let semestreSelect = this.semestres.find(semestre => semestre.id.toString() === semestreId.toString());
            if (semestreSelect) {
                return semestreSelect.label;
            } 
        },

        getCursoName(cursoId) {
            let cursoSelect = this.cursos.find(curso => curso.id === cursoId);
            if (cursoSelect) {
                return cursoSelect.label;
            }         
        },
        getDisciplinaName(disciplinaId) {
            let disciplinaSelect = this.disciplinas.find(disciplina => disciplina.id.toString() === disciplinaId.toString());
            if (disciplinaSelect) {
                return disciplinaSelect.label;
            }
        },
        getAmbienteName(ambienteId) {
            let ambienteSelect = this.ambientes.find(ambiente => ambiente.id.toString() === ambienteId.toString());
            if (ambienteSelect) {
                return ambienteSelect.label;
            } 
        },

        customizeAmbiente() {
            $("#semestre").select2({
                placeholder: "Semestres...",
                templateSelection: function (data) {
                    const style = 'style="color: #7D848B; "';

                    return $(
                        "<span " +
                            style +
                            ">" +
                            "<i class='icon icon-calendario-semestre'></i> " + data.text  +"</span> "
                    );
                },
            });
            $("#disciplina").select2({
                placeholder: "Disciplinas...",
                templateSelection: function (data) {
                    let style = 'style="color: #7D848B; "';
                    return $(
                        "<span " + style + ">" + "<i class='icon icon-disciplina' ></i> " + data.text + "</span> "
                    );
                },
            });
            $("#curso").select2({
                placeholder: "Cursos...",
                templateSelection: function (data) {
                    const style = 'style="color: #7D848B; "';
                    return $("<span " + style + ">" + "<i class='icon icon-icone-ava'></i> " + data.text + "</span> ");
                },
            });
            $("#ambiente").select2({
                placeholder: "Ambientes...",
                templateSelection: function(data) {
                    let style = 'style="color: #7D848B; "';
                    return $("<span " + style + ">" + "<i class='icon icon-moodle'></i> " + data.text + "</span>");
                },
            });
            $("#situacao").select2({
                templateSelection: function (data) {
                    
                    const style = 'style="padding: 0 5px 0 0px; color: #7D848B; "';
                    return $("<span " + style + ">" + data.text  + "</span> ");
                },
            });
        },

        handleSelectChange(event) {
            let selectedValue = event.target.value;
            let courseList = document.getElementById("course-list");
            let navDiario = document.getElementById("nav-diarios");
            let navCoordenacoes = document.getElementById("nav-coordenacoes");

            if (selectedValue == "diarios") {
                navCoordenacoes.classList.remove("show", "active");
                navDiario.classList.add("show", "active");
            } else if (selectedValue == "coordenacoes") {
                var courseShortnames = document.getElementsByClassName("course-shortname");
                for (var i = 0; i < courseShortnames.length; i++) {
                    courseShortnames[i].style.paddingLeft = "10px";
                }

                navDiario.classList.remove("show", "active");
                navCoordenacoes.classList.add("show", "active");
            }
        },

        openPopup() {
            this.isPopupOpen = true;
            document.body.style.overflow = "hidden";
            document.body.classList.add("open");
        },
        closePopup() {
            this.isPopupOpen = false;
            document.body.style.overflow = "auto";
            document.body.classList.remove("open");
        },

        popup() {
            $(function () {
                if (!window.popupModalName) {
                    return;
                }
                const lastOccurrence = new Date(localStorage.getItem(window.popupModalName));

                // Já respondeu
                if (isNaN(lastOccurrence)) {
                    return;
                }

                // O popup nunca foi visto ou se passaram 12h desde a última visualização sem responder
                if ((new Date() - lastOccurrence) / (1000 * 3600 * 12) > 1) {
                    new bootstrap.Modal(document.getElementById(popupModalName)).toggle();
                }

                // Se fechar sem clicar no link pede para repetir em 12h
                $("#" + popupModalName).on("hidden.bs.modal", function () {
                    localStorage.setItem(popupModalName, new Date().toISOString());
                    console.log("closeModalUntilTomorrow");
                });

                $("#model-url").on("click", function closeModalForever(e) {
                    $("#modal1").click();
                    localStorage.setItem(popupModalName, "true");
                    window.open(popupModalUrl);
                });
            });
        },

        favourite(card) {
            const new_status = card.isfavourite ? 0 : 1;
            let situacao = ($("#situacao").val())
            axios
                .get("/painel/api/v1/set_favourite/", {
                    params: {
                        ava: card.ambiente.titulo,
                        courseid: card.id,
                        favourite: new_status,
                    },
                })
                .then((response) => {
                    
                    card.isfavourite = new_status == 1;
                    setTimeout(() => {
                        if (situacao == "favourites") {
                            this.filterCards();
                        }
                    }, 500); 
                })

                
                .catch((error) => {
                    console.debug(error);
                });
        },

        visible(card) {
            if (confirm("Confirma a operação?")) {
                const new_status = parseInt(card.visible) ? 0 : 1;
                axios
                    .get("/painel/api/v1/set_visible/", {
                        params: {
                            ava: card.ambiente.titulo,
                            courseid: card.id,
                            visible: new_status,
                        },
                    })
                    .then((response) => {
                        card.visible = new_status == 1;
                    })
                    .catch((error) => {
                        console.debug(error);
                    });
            }
        },

        cardActionsToggler(event) {
            let item = $(event.currentTarget).parent().parent().parent();
            
            let icon = $(event.currentTarget).find("i");
            let label = icon.closest("label");
            let situacao = $("#situacao").val();  // Certifique-se de que situacao está acessível aqui
            

            // Toggle classes for changing color
            if ($(item).hasClass("showActions")) {
                $(item).removeClass("showActions");
                $(label).removeClass("favorited seta seta-up").addClass("seta seta-down");
            } else {
                $(item).addClass("showActions");
                $(label).removeClass("seta seta-down").addClass("favorited seta seta-up");

            }
        },
        async clearFilter() {
            await this.updateFilterValues("inprogress");

            this.filterCards();
        },
        async updateFilterValues(situacao) {
            //resetar os valores tanto visualmente como no localStorage
            $("#q").val("").trigger("change");
            $("#situacao").val(situacao).trigger("change");
            $("#semestre").val("").trigger("change");
            $("#disciplina").val("").trigger("change");
            $("#curso").val("").trigger("change");
            $("#ambiente").val("").trigger("change");

            $(".select2-selection").removeClass("bgcolor-select2");
            $('#semestre, #disciplina, #curso').prop('disabled', false).removeClass('disabled-background');


            this["q"] = "";
            this["situacao"] = situacao;
            this["semestre"] = "";
            this["disciplina"] = "";
            this["curso"] = ""; 
            this["ambiente"] = "";
        },

        setValueFields() {
            //para setar os valores escolhidos no localStorage
            //this["q"] = $(self.q).val() || localStorage.q || "";
            this["situacao"] = $("#situacao").val() || localStorage.situacao || "inprogress";
            this["semestre"] = $("#semestre").val() || localStorage.semestre || "";
            this["disciplina"] = $("#disciplina").val() || localStorage.disciplina || "";
            this["curso"] = $("#curso").val() || localStorage.curso || "";
            this["ambiente"] = $("#ambiente").val() || localStorage.ambiente || "";
        },

        clearOneValue(campo) {
            if (campo === "semestre") {
                localStorage.semestre = '';
                $("#semestre").val("").trigger("change");
            } else if (campo === "disciplina") {
                localStorage.disciplina = '';
                $("#disciplina").val("").trigger("change");
            } else if (campo === "curso") {
                localStorage.curso = '';
                $("#curso").val("").trigger("change");
            } else if (campo === "ambiente") {
                localStorage.ambiente = '';
                $("#ambiente").val("").trigger("change");
            }
            $('#semestre, #disciplina, #curso').prop('disabled', false).removeClass('disabled-background');

            this.filterCards();
        },

        filterCards() {
            this.filtering();                                 
            try {
                axios
                    .get("/painel/api/v1/diarios/", {
                        params: {
                            q: $(self.q).val() || localStorage.q || "",
                            situacao: $("#situacao").val() || localStorage.situacao || "inprogress",
                            semestre: $("#semestre").val() || localStorage.semestre || "",
                            disciplina: $("#disciplina").val() || localStorage.disciplina || "",
                            curso: $("#curso").val() || localStorage.curso || "",
                            ambiente: $("#ambiente").val() || localStorage.ambiente || "",
                        },
                    })
                    .then((response) => {
                        Object.assign(this, response.data);
                        this.filtered();
                    })
                    .catch((error) => {
                        this.has_error = true;
                        this.filtered();
                        return Promise.reject(error);
                    });
            } catch (e) {
                console.debug(e);
                this.has_error = true;
                this.filtered();
            }
            this.setValueFields();
        },

        filtering() {
            this.diarios = [];
            this.coordenacoes = [];
            this.praticas = [];
            this.reutilizaveis = [];
            this.has_error = false;
            this.is_filtering = true;
        },

        filtered() {
            //this.restoreState();
            this.is_filtering = false;
            $("#semestre").select2("val", localStorage.getItem('semestre'));
        },

        get_situacao_desc() {
            return $("#situacao option:selected").text();
        },

        go_to_suap() {
            $("#syncs").modal("show");
        },

        go_to_coordanation() {
            $("#syncs").modal("show");
        },

        go_to_grades() {
            $("#syncs").modal("show");
        },

        go_to_grades_preview() {
            $("#syncs").modal("show");
        },

        go_to_sync_logs() {
            $("#syncs").modal("show");
        },

        isFromSUAP(diario) {
            return diario != null && Object.hasOwn(diario, "id_diario_clean");
        },
        handleResize() {
            this.screenWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
        },
    },

    watch: {
        q(newValue) {
            localStorage.q = newValue || "";
            //console.log('O valor de Q mudou para:', newValue);
        },
        situacao(newValue) {
            localStorage.situacao = newValue || "inprogress";
            //console.log('O valor de Situação mudou para:', newValue);
        },
        semestre(newValue) {
            localStorage.semestre = newValue || "";
            //console.log('O valor de Semestre mudou para:', newValue);
        },
        disciplina(newValue) {
            localStorage.disciplina = newValue || "";
            //console.log('O valor de Disciplina mudou para:', newValue);
        },
        curso(newValue) {
            localStorage.curso = newValue || "";
            //console.log('O valor de Curso mudou para:', newValue);
        },
        ambiente(newValue) {
            localStorage.ambiente = newValue || "";
            //console.log('O valor de Ambiente mudou para:', newValue);
        },
    },
};
