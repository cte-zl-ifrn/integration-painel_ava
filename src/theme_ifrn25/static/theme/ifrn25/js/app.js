import * as VueSelect from './vue-select.js';

const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    components: {
        'v-select': VueSelect.default,
    },
    data() {
        return {
            isBottom: window.INITIAL_SETTINGS.menuPosition === 'bottom',
            sidebarContracted: false,
            modalOpen: false,
            accessibilityModalOpen: false,
            helpModalOpen: false,
            notificationsModalOpen: false,
            messagesModalOpen: false,
            filterModalOpen: false,
            profileModalOpen: false,
            modalHeaderIcons: {
                accessibility: 'fa-universal-access',
                help: 'fa-question-circle',
                notifications: 'fa-bell',
                messages: 'fa-comment',
                filter: 'fa-filter',
                profile: 'fa-user',
            },
            modalHeaderIcon: '',
            modalType: '',
            modalTitle: '',
            activeTab: 0,
            tabs: [
                { desktop: 'Meus Diários', mobile: 'Diários' }, 
                { desktop: 'Salas de Coordenação', mobile: 'Coordenações' }, 
                { desktop: 'Práticas', mobile: 'Práticas'}, 
                { desktop: 'Reutilizar', mobile: 'Reutilizar'},
            ],
            filters: {
                situacao: 'inprogress',
                semestre: null,
                periodo: null,
                modulo: null,
                disciplina: null,
                curso: null,
                ambiente: null,
                query: null,
            },

            splideInstance: null,
            selectedMessageOption: 'all',
            messageOptions: [
                { label: 'Todos', value: 'all' },
                { label: 'Não lidas', value: 'unread' },
                { label: 'Grupos', value: 'groups' },
                { label: 'Favoritos', value: 'favorites' },
                { label: 'Privado', value: 'private' }
            ],
            preferences: {
                dyslexia_friendly: false,
                big_cursor: false,
                vlibras_active: true,
                highlight_links: false,
                stop_animations: false,
                hidden_illustrative_image: false,
                remove_justify: false,
                high_line_height: false,
                zoom_level: '100',
                zoom_options: ['100', '120', '130', '150', '160'],
                color_mode: 'default',
                color_mode_options: ['default', 'high_contrast', 'low_contrast', 'colorblind', 'grayscale'],
            },
            messages: [
                // { id: 1, receiver: 'Ronaldo', sender: '', content: 'Conteúdo da mensagem 1', date: '2023-03-25 12:00', read: false, favorite: true, group: '', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8E7wlGmOb1_0GI4vqlvieVWlGdkMW5Mv0XQ&s' },
                // { id: 2, receiver: '', sender: 'Messi', content: 'Conteúdo da mensagem 22222222222222222222222222222222222222222222222222', date: '2023-01-02 14:00', read: true, favorite: true, group: 'Grupo A', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxLoJONSCCuN_JBwM_xVD5hloPBf4pHB9R7A&s' },
                // { id: 3, receiver: 'Neymar', sender: '', content: 'Conteúdo da mensagem 3', date: '2023-01-03 16:00', read: false, favorite: false, group: 'Grupo B', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNMnJ3i8BARfyzD9fxQ9GvorEDF1gTrZqzrA&s' },
                // { id: 4, receiver: '', sender: 'Cristiano Ronaldo', content: 'Conteúdo da mensagem 44444444444444', date: '2023-01-04 18:00', read: true, favorite: true, group: '', img: 'https://img.a.transfermarkt.technology/portrait/big/8198-1694609670.jpg?lm=1' },
                // { id: 5, receiver: 'Zidane', sender: '', content: 'Conteúdo da mensagem 5', date: '2023-03-25 20:00', read: false, favorite: false, group: 'Grupo A', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoSDG52Efy_SkQKqp9tTaS46NaaZCNEX2LJQ&s' },
                // { id: 6, receiver: 'Ronaldinho', sender: '', content: 'Conteúdo da mensagem 6666666666666', date: '2023-03-25 12:00', read: true, favorite: true, group: 'Grupo A', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSioEdBrFFM0iW0f6uhegsUMeMptl48GSdOeQ&s' },
            ],
            messageSearchQuery: '',
            notifications: [
                // { id: 1, title: 'Notificação 1', date: '2025-03-25 12:00', link: '#' },
                // { id: 2, title: 'Notificação 2', date: '2025-01-02 14:00', link: '#' },
                // { id: 3, title: 'Notificação 3', date: '2025-01-03 16:00', link: '#' },
                // { id: 4, title: 'Notificação 4', date: '2025-01-04 18:00', link: '#' },
                // { id: 5, title: 'Notificação 5', date: '2025-03-25 20:00', link: '#' },
                // { id: 6, title: 'Notificação 6', date: '2025-03-21 12:00', link: '#' },
                // { id: 7, title: 'Notificação 9', date: '2025-03-25 12:00', link: '#' },
            ],
            periodos: [],
            modulos: [],
            semestres: [],
            situacoes: [
                { label: "Diários em andamento", id: "inprogress" },
                { label: "Diários a iniciar", id: "future" },
                { label: "Encerrados pelo professor", id: "past" },
                { label: "Meus diários favoritos", id: "favourites" },
                { label: "Todos os diários (lento)", id: "allincludinghidden" },
            ],
            disciplinas: [],
            cursos: [],
            ambientes: [],
            coordenacoes: [],
            praticas: [],
            diarios: [],
            salas: [],
            reutilizaveis: [],
            loading: false,
        };
    },
    watch: {
        messagesModalOpen(newVal) {
            if (newVal) {
                this.$nextTick(() => {
                    this.initSplide();
                    this.splideInstance.refresh();
                });
            } else {
                if (this.splideInstance) {
                    this.splideInstance.destroy();
                }
            }
        },
        filters: {
            handler() {
                // this.filterCards();
                console.log('Filters changed:', this.filters);
                localStorage.setItem('filters', JSON.stringify(this.filters));
            },
            deep: true // Observa mudanças profundas no objeto
        }
    },
    computed: {
        visibleTabs() {
            return this.tabs
              .map((tab, index) => ({
                ...tab, 
                originalIndex: index
              }))
              .filter(tabItem => {
                // Abas 0 (Meus Diários) e 1 (Salas de Coordenação) são sempre visíveis
                if (tabItem.originalIndex === 0 || tabItem.originalIndex === 1) {
                  return true;
                }
                // Aba 2 (Práticas) só é visível se praticas.length > 0
                if (tabItem.originalIndex === 2 && this.praticas.length > 0) {
                  return true;
                }
                // Aba 3 (Reutilizar) só é visível se reutilizaveis.length > 0
                if (tabItem.originalIndex === 3 && this.reutilizaveis.length > 0) {
                  return true;
                }

                return false;
              });
        },

        filteredMessages() {
            const searchQuery = this.messageSearchQuery.toLowerCase();
            
            return this.messages.filter(msg => {
                // Filtro por tipo de mensagem
                let matchesType = false;
                switch (this.selectedMessageOption) {
                    case 'all': matchesType = true; break;
                    case 'unread': matchesType = !msg.read; break;
                    case 'groups': matchesType = msg.group !== ''; break;
                    case 'favorites': matchesType = msg.favorite; break;
                    case 'private': matchesType = msg.group === ''; break;
                    default: matchesType = true;
                }
    
                // Filtro por busca textual
                const matchesSearch = !searchQuery || 
                    (msg.sender && msg.sender.toLowerCase().includes(searchQuery)) ||
                    (msg.receiver && msg.receiver.toLowerCase().includes(searchQuery));
    
                return matchesType && matchesSearch;
            });
        },
        activeFilters() {
            const filterTypes = [
                { key: 'situacao', options: this.situacoes, icon: 'fa-book' },
                { key: 'semestre', options: this.semestres, icon: 'fa-calendar-days' },
                { key: 'periodo', options: this.periodos, icon: 'fa-calendar-week' },
                { key: 'modulo', options: this.modulos, icon: 'fa-calendar-day' },
                { key: 'disciplina', options: this.disciplinas, icon: 'fa-newspaper' },
                { key: 'curso', options: this.cursos, icon: 'cursos' },
                { key: 'ambiente', options: this.ambientes, icon: 'ambientes' }
            ];
            return filterTypes.reduce((acc, { key, options, icon }) => {
                const value = this.filters[key];
                if (value) {
                    const option = options.find(o => o.id === value);
                    if (option) {
                    acc.push({
                        type: key,
                        label: option.label,
                        value: value,
                        icon: icon
                    });
                    }
                }
                return acc;
            }, []);
        }
    },
    mounted() {
        this.clearGauge();
        this.getPreferences();
        this.loadFilters();
        this.filterCards();
        this.sidebarContracted = this.isMobile();
    },
    methods: {
        getPreferences() {
            if (document.body.classList.contains('dyslexia_friendly')) {
                this.preferences.dyslexia_friendly = true;
            }
            if (document.body.classList.contains('big_cursor')) {
                this.preferences.big_cursor = true;
            }
            if (!document.body.classList.contains('vlibras_active')) {
                this.preferences.vlibras_active = false;
            }            
            if (document.body.classList.contains('highlight_links')) {
                this.preferences.highlight_links = true;
            }
            if (document.body.classList.contains('stop_animations')) {
                this.preferences.stop_animations = true;
            }
            if (document.body.classList.contains('hidden_illustrative_image')) {
                this.preferences.hidden_illustrative_image = true;
            }
            if (document.body.classList.contains('remove_justify')) {
                this.preferences.remove_justify = true;
            }
            if (document.body.classList.contains('high_line_height')) {
                this.preferences.high_line_height = true;
            }

            const zoom = document.body.getAttribute('data-zoom');
            if (zoom) {
                this.preferences.zoom_level = zoom;
            }   

            const bodyClassList = document.body.classList;
            const colorModeClass = [...bodyClassList].find(c => c.startsWith('color-mode-'));

            if (colorModeClass) {
                this.preferences.color_mode = colorModeClass.replace('color-mode-', '');
            }
        },
        async savePosition() {
            const pos = this.isBottom ? 'bottom' : 'top';
            const app = document.getElementById('app');
            try {
                await axios.post(
                '/settings/menu-position/',
                new URLSearchParams({ position: pos }),
                { headers: { 'X-CSRFToken': this.getCsrfToken() } }
                );
                app.classList.toggle('menu-bottom', this.isBottom);
            } catch (err) {
                console.error('Não foi possível salvar a posição:', err);
            }
        },
        getCsrfToken() {
            const token = document.cookie
                .split(';')
                .map(c => c.trim())
                .find(c => c.startsWith('csrftoken='));

            return token ? token.split('=')[1] : '';
        },
        initSplide() {
            if (this.splideInstance) {
                this.splideInstance.destroy();
            }
            this.$nextTick(() => {
                if (typeof Splide !== 'undefined') {
                    this.splideInstance = new Splide('.splide', {
                        type: 'slide',
                        perPage: 1,
                        pagination: false,
                        autoWidth: true,
                        arrows: false,
                        drag: 'free',
                        wheel: true,
                        releaseWheel: true,
                        speed: 600,
                        wheelSleep: 300,
                        wheelMinThreshold: 20,
                        gap: '5px',
                        breakpoints: {
                            768: {
                                perPage: 2,
                            },
                            480: {
                                perPage: 1,
                            }
                        }
                    }).mount();
                }
            });
        },
        formatDateForMessages(dateString) {
            const messageDate = new Date(dateString);
            const today = new Date();
            if (messageDate.toDateString() === today.toDateString()) {
                return messageDate.toLocaleTimeString('pt-BR', {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            }
            return messageDate.toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        },
        formatDateForNotifications(dateString) {
            const notificationDate = new Date(dateString);
            const now = new Date();
            const diffInMilliseconds = now - notificationDate;
            const diffInMinutes = Math.floor(diffInMilliseconds / (1000 * 60));
            const diffInHours = Math.floor(diffInMinutes / 60);
            const diffInDays = Math.floor(diffInHours / 24);
            if (diffInDays > 0) return `${diffInDays} dias atrás`;
            if (diffInHours > 0) return `${diffInHours} horas atrás`;
            return `${diffInMinutes} minutos atrás`;
        },
        selectMessageOption(value) {
            this.selectedMessageOption = value;  
            if (this.splideInstance) {
                this.splideInstance.refresh();
            }
        },
        isMobile() {
            return window.innerWidth < 768
        },
        toggleModalWithContent(type) {
            if (this.isMobile()) {
                this.closeSidebar();
            }
            if (this.modalOpen && this.modalType === type) {
                this.modalType = null;
                this.modalOpen = false;
                return;
            }
            if(this.modalOpen && this.modalType !== type) {
                this.modalOpen = false;
                setTimeout(() => {
                    this.modalType = type;
                    this.modalTitle = this.getModalTitle(type);
                    this.modalHeaderIcon = this.modalHeaderIcons[type];
                    this.modalOpen = true;
                }, 200);
                return;
            }
            this.modalType = type;
            this.modalTitle = this.getModalTitle(type);
            this.modalHeaderIcon = this.modalHeaderIcons[type];
            this.modalOpen = true;

        },
        getModalTitle(type) {
            switch (type) {
                case 'accessibility':
                    this.accessibilityModalOpen = true;
                    this.helpModalOpen = false;
                    this.notificationsModalOpen = false;
                    this.messagesModalOpen = false;
                    this.filterModalOpen = false;
                    this.profileModalOpen = false;
                    return 'Acessibilidade';
                case 'help':
                    this.helpModalOpen = true;
                    this.accessibilityModalOpen = false;
                    this.notificationsModalOpen = false;
                    this.messagesModalOpen = false;
                    this.filterModalOpen = false;
                    this.profileModalOpen = false;
                    return 'Ajuda';
                case 'notifications':
                    this.notificationsModalOpen = true;
                    this.accessibilityModalOpen = false;
                    this.helpModalOpen = false;
                    this.messagesModalOpen = false;
                    this.filterModalOpen = false;
                    this.profileModalOpen = false;
                    return 'Notificações';
                case 'messages':
                    this.messagesModalOpen = true;
                    this.accessibilityModalOpen = false;
                    this.helpModalOpen = false;
                    this.notificationsModalOpen = false;
                    this.filterModalOpen = false;
                    this.profileModalOpen = false;
                    return 'Mensagens';
                case 'filter':
                    this.filterModalOpen = true;
                    this.accessibilityModalOpen = false;
                    this.helpModalOpen = false;
                    this.notificationsModalOpen = false;
                    this.messagesModalOpen = false;
                    this.profileModalOpen = false;
                    return 'Filtros';
                case 'profile':
                    this.profileModalOpen = true;
                    this.accessibilityModalOpen = false;
                    this.helpModalOpen = false;
                    this.notificationsModalOpen = false;
                    this.messagesModalOpen = false;
                    this.filterModalOpen = false;
                    this.profileModalOpen = false;
                    return 'Menu do Usuário';
                default:
                    return '';
            }
        },
        toggleSidebar() {
            if (this.isMobile()) {
                this.closeSidebarModal();
            }
            this.sidebarContracted = !this.sidebarContracted
        },
        closeSidebar() {
            this.sidebarContracted = true;
        },
        closeSidebarModal() {
            this.modalOpen = false;
            this.modalType = '';
            this.modalTitle = '';
            this.modalHeaderIcon = '';
        },
        closeSidebarAndModal() {
            this.closeSidebar();
            this.closeSidebarModal();
        },
        setActiveTab(index) {
            this.activeTab = index;
        },
        async filterCards() {
            // Modal fecha ao fazer busca no mobile
            if(this.isMobile()) {
                this.closeSidebarModal();
            }
            this.loading = true;
            try {
                const params = new URLSearchParams({
                    q: this.filters.query || "",
                    situacao: this.filters.situacao,
                    semestre: this.filters.semestre || "",
                    disciplina: this.filters.disciplina || "",
                    curso: this.filters.curso || "",
                    ambiente: this.filters.ambiente || "",
                });

                const res = await fetch(`/api/v1/diarios/?${params.toString()}`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();

                this.handleFilterResponse(data);
            } catch (error) {
                console.error("Error fetching data:", error);
                this.diarios = [];
            } finally {
                this.loading = false;
            }
        },
        handleFilterResponse(data) {
            if (data.diarios && Array.isArray(data.diarios)) {
                this.diarios = data.diarios.map(diario => ({
                    id: diario.id,
                    fullname: diario.fullname,
                    shortname: this.changeShortnameStyle(diario.shortname),
                    isfavourite: diario.isfavourite,
                    environment: diario.ambiente.titulo,
                    progress: diario.progress,
                    visible: diario.visible == 1,
                    can_set_visibility: diario.can_set_visibility,
                    url: diario.viewurl
                }));
            } else {
                this.diarios = [];
            }
            if (data.coordenacoes && Array.isArray(data.coordenacoes)) {
                this.coordenacoes = data.coordenacoes.map(coordenacao => ({
                    id: coordenacao.id,
                    fullname: coordenacao.fullname,
                    shortname: coordenacao.shortname,
                    isfavourite: coordenacao.isfavourite,
                    environment: coordenacao.ambiente.titulo,
                    progress: coordenacao.progress,
                    visible: coordenacao.visible == 1,
                    can_set_visibility: coordenacao.can_set_visibility,
                    url: coordenacao.viewurl
                }));
            }
            else {
                this.coordenacoes = [];
            }
            // if (data.praticas && Array.isArray(data.praticas)) {
            //     this.praticas = data.praticas.map(sala => ({
            //         id: sala.id,
            //         fullname: sala.fullname,
            //         shortname: sala.shortname,
            //         isfavourite: sala.isfavourite,
            //         environment: sala.ambiente.titulo,
            //         progress: sala.progress,
            //         visible: sala.visible,
            //         url: sala.viewurl
            //     }));
            // }
            // else {
            //     this.praticas = [];
            // }
            // if (data.reutilizaveis && Array.isArray(data.reutilizaveis)) {
            //     this.reutilizaveis = data.reutilizaveis.map(sala => ({
            //         id: sala.id,
            //         fullname: sala.fullname,
            //         shortname: sala.shortname,
            //         isfavourite: sala.isfavourite,
            //         environment: sala.ambiente.titulo,
            //         progress: sala.progress,
            //         visible: sala.visible,
            //         url: sala.viewurl
            //     }));
            // }
            // else {
            //     this.reutilizaveis = [];
            // }
            
            // if (data.modulos && Array.isArray(data.modulos)) {
            //     this.modulos = data.modulos.map(modulo => ({
            //         id: modulo.id,
            //         label: modulo.label
            //     }));
            // }
            // else {
            //     this.modulos = [];
            // }
            
            if (data.periodos && Array.isArray(data.periodos)) {
                this.periodos = data.periodos.slice(1).map(periodo => ({
                    id: periodo.id,
                    label: periodo.label
                }));
            }
            else {
                this.periodos = [];
            }
            if (data.semestres && Array.isArray(data.semestres)) {
                this.semestres = data.semestres.slice(1).map(semestre => ({
                    id: semestre.id,
                    label: semestre.label
                }));
            }
            else {
                this.semestres = [];
            }
            if (data.disciplinas && Array.isArray(data.disciplinas)) {
                this.disciplinas = data.disciplinas.slice(1).map(disciplina => ({
                    id: disciplina.id,
                    label: disciplina.label
                }));
            }
            else {
                this.disciplinas = [];
            }
            if (data.cursos && Array.isArray(data.cursos)) {
                this.cursos = data.cursos.slice(1).map(curso => ({
                    id: curso.id,
                    label: curso.label
                }));
            }
            else {
                this.cursos = [];
            }
            if (data.ambientes && Array.isArray(data.ambientes)) {
                this.ambientes = data.ambientes.slice(1).map(ambiente => ({
                    id: ambiente.id,
                    label: ambiente.label
                }));
            }
            else {
                this.ambientes = [];
            }
            this.userTour01();

        },
        removeFilter(filterType) {
            if (filterType === 'situacao') return; // Impede remoção do filtro padrão
            this.filters[filterType] = null;
            this.filterCards();
        },
        resetFilters() {
            this.filters = {
                situacao: 'inprogress',
                semestre: null,
                periodo: null,
                modulo: null,
                disciplina: null,
                curso: null,
                ambiente: null
            };
            this.saveFilters();
            this.filterCards();
        },
        saveFilters() {
            localStorage.setItem('filters', JSON.stringify(this.filters));
        },
        loadFilters() {
            const savedFilters = localStorage.getItem('filters');
            if (savedFilters) {
                try {
                    const parsedFilters = JSON.parse(savedFilters);
                    this.filters = {
                        ...this.filters, // Valores padrão
                        ...parsedFilters // Sobrescreve com os salvos
                    };
                } catch (e) {
                    console.error('Erro ao carregar filtros:', e);
                }
            }
        },
        changeShortnameStyle(shortname) {
            shortname = shortname.trim();
            const regexShortname = /^(\d+\.\d+\.\d+\.\w+)\.(\w+\.\d+)(#\d+)?$/;
            const match = shortname.match(regexShortname);

            if (match) {
                const grupo1 = match[1];
                const grupo2 = match[2];
                const grupo3 = match[3] || '';
                return `${grupo1} ${grupo2} ${grupo3}`.trim();
            } else {
                return shortname;
            }
        },
        canToggleVisible(card) {
            axios
                .get("/api/v1/set_visible/", {
                    params: {
                        ava: card.ambiente.titulo,
                        courseid: card.id,
                        visible: card.visible,
                    },
                })
                .then(() => {
                    return true;
                })
                .catch((error) => {
                    return false;
                });
        },
        toggleVisible(card) {
            const action = card.visible ? "ocultar" : "publicar";

            this.showConfirmation(action, (confirmed) => {
                if (confirmed) {
                    const new_status = card.visible ? '0' : '1';
                    axios
                        .get("/api/v1/set_visible/", {
                            params: {
                                ava: card.environment,
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
            });
        },
        toggleFavourite(item) {
            const new_status = item.isfavourite ? 0 : 1;
            const params = new URLSearchParams({
                ava: item.environment,
                courseid: item.id,
                favourite: new_status,
            });
            
            fetch(`/api/v1/set_favourite/?${params.toString()}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                item.isfavourite = new_status === 1;
            })
            .catch(error => {
                console.error('Erro ao atualizar favorito:', error);
            });
        },
        togglePreference(category, key, value) {
            const params = new URLSearchParams({
                category: category,
                key: key,
                value: value
            });

            fetch(`/api/v1/set_user_preference/?${params.toString()}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erro HTTP! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        console.error("Erro ao atualizar preferência:", data.error.message);
                        return;
                    }

                    // Atualiza a UI conforme a preferência
                    if (key === "zoom_level") {
                        document.body.setAttribute("data-zoom", value);
                        return;
                    } 

                    if (key === "color_mode") {
                        const modes = this.preferences.color_mode_options;

                        // remove todos
                        modes.forEach(m => {
                            document.body.classList.remove(`color-mode-${m}`);
                        });

                        // adiciona o selecionado
                        document.body.classList.add(`color-mode-${value}`);
                        return;
                    }
                    
                    document.body.classList.toggle(key, value === true || value === "true");
                })
                .catch(error => {
                    console.error("Erro na requisição:", error);
            });
        },
        cycleAccessibility() {
            const currentIndex = this.preferences.zoom_options.indexOf(this.preferences.zoom_level);
            const nextIndex = (currentIndex + 1) % this.preferences.zoom_options.length;
            this.preferences.zoom_level = this.preferences.zoom_options[nextIndex];
            this.togglePreference('accessibility', 'zoom_level', this.preferences.zoom_level);
        },
        cycleColorMode() {
            const modes = this.preferences.color_mode_options;
            const current = this.preferences.color_mode;

            const currentIndex = modes.indexOf(current);
            const nextIndex = (currentIndex + 1) % modes.length;

            const next = modes[nextIndex];
            this.preferences.color_mode = next;

            // Salva no Moodle / backend
            this.togglePreference('accessibility', 'color_mode', next);
        },
        colorModeLabel(mode) {
            switch (mode) {
                case 'default': return 'Padrão';
                case 'high_contrast': return 'Alto contraste';
                case 'low_contrast': return 'Contraste reduzido';
                case 'colorblind': return 'Amigável a daltônicos';
                case 'grayscale': return 'Escala de cinza';
                default: return mode;
            }
        },
        goToCourse(item) {
            window.location.href = item.url;
        },
        goToCourseUrl(item) {
          return item.url;
        },
        mostrarGauge(e) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';

            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';

            const text = document.createElement('div');
            text.className = 'loading-text';
            text.textContent = 'Carregando, aguarde...';

            // insere dentro do overlay
            overlay.appendChild(spinner);
            overlay.appendChild(text);

            // adiciona overlay ao body
            document.body.appendChild(overlay);
        },
        clearGauge() {
            window.addEventListener("pageshow", (event) => {
                if (event.persisted) {
                    const overlay = document.querySelector('.loading-overlay');
                    if (overlay) overlay.remove();
                } 
            })
        },
        showConfirmation(action, callback) {
            const modal = document.getElementById("popup-modal");
            const title = document.getElementById("popup-modal-message-title");
            const message = document.getElementById("popup-modal-message");
            const confirmBtn = document.getElementById("modal-confirm");
            const cancelBtn = document.getElementById("modal-cancel");
            const modalContent = modal.querySelector(".popup-modal-content");

            title.innerHTML = `Gostaria de <strong>${action}</strong> esse diário?`;
            if(action == 'publicar') {
                message.innerHTML = `Ao publicar este diário os alunos terão acesso ao conteúdo`;
            }
            if(action == 'ocultar') {
                message.innerHTML = `Ao ocultar este diário os alunos <strong>não</strong> terão acesso ao conteúdo`;
            }
            modal.classList.remove("hidden");

            const closeModal = (confirmed) => {
                modal.classList.add("hidden");
                confirmBtn.removeEventListener("click", confirmHandler);
                cancelBtn.removeEventListener("click", cancelHandler);
                modal.removeEventListener("click", outsideClickHandler);
                callback(confirmed);
            };

            const confirmHandler = () => closeModal(true);
            const cancelHandler = () => closeModal(false);

            // Fecha ao clicar fora do conteúdo do modal
            const outsideClickHandler = (event) => {
                if (!modalContent.contains(event.target)) {
                    closeModal(false);
                }
            };

            confirmBtn.addEventListener("click", confirmHandler);
            cancelBtn.addEventListener("click", cancelHandler);
            modal.addEventListener("click", outsideClickHandler);
        },

        userTour01() {
            if (localStorage.getItem("completou-user-tour01") != "true") {
                const dicaPadrao = "<p style='text-align: center'><b>Você SEMPRE pode clicar na área destacada para testar.</b></p>";
                const steps = [
                    {
                        element: ".topbar",
                        title: "Aqui estão suas salas",
                        content: "<p>Você pode acessar seus diários, salas de coordenação, salas de práticas e reutilizáveis.</p><p>Clique em cada aba para ver a lista de salas.</p>" + dicaPadrao,
                        placement: "bottom-start",
                    },
                    {
                        element: "#btn-toggle-sidebar",
                        title: "Gaveta de menus",
                        content: '<p>Seus menus estão todos de gaveta que você pode abrir e fechar o quanto quiser.</p><p>Clique em <button id="btn-toggle-sidebar-usertour" onclick="document.getElementById(\'btn-toggle-sidebar\').click();" style="background-color: var(--verde-escuro);color: #fff;border-radius: 5px;padding: 0 5px;">&lt;&gt;</button> para alternar.</p>',
                        placement: "bottom-start",
                        onNext: () => {
                            try {
                                const elemento = document.getElementById('btn-toggle-filter');
                                if (elemento && !elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }
                        }
                    },
                    {
                        element: "#btn-toggle-filter",
                        title: "Filtros",
                        content: "<p>Não localizou a sala? Experimente alterar os filtros.</p>",
                        placement: "bottom-start",
                        onPrevious: () => {
                            try {
                                const elemento = document.getElementById('btn-toggle-filter');
                                if (elemento && !elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }
                        },
                        onNext: () => {
                            try {
                                const elemento = document.getElementById('btn-toggle-accessibility');
                                if (elemento && !elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }
                        },
                    },
                    {
                        element: "#btn-toggle-accessibility",
                        title: "Acessibilidade",
                        content: "<p>Aqui você pode deixar a fonte mais acessível para disléxicos.</p><p>Continuamos trabalhando para adicionar recursos de acessibilidade.</p>",
                        placement: "top-start",
                        onPrevious: () => {
                            try {
                                const elemento = document.getElementById('btn-toggle-filter');
                                if (elemento && !elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }
                        },

                        onNext: () => {
                            try {
                                const elemento = document.getElementById('btn-toggle-help');
                                if (elemento && !elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }
                        }
                    },
                    {
                        element: "#btn-toggle-help",
                        title: "Ainda precisa de ajuda?",
                        content: "<ul>" +
                                "<li>Acesse nossa <b>Central de Ajuda</b> para tirar dúvidas das mais diversas.</li>" +
                                "<li>Tenha seus direitos protegidos pela <b>Ouvidoria</b> do IFRN.</li>" +
                                "<li>Use nossa lista de <b>contatos</b> caso precise entrar em contato por telefone.</li>" +
                                "<li>Necessita de um atendimento para uma demanda? Use uma das nossas <b>Centrais de Atendimento</b> no SUAP.</li>" +
                                "</ul>",
                        placement: "top-start",
                        onPrevious: () => {
                            try {
                                const elemento = document.getElementById('btn-toggle-accessibility');
                                if (elemento && !elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }
                        },
                        onNext: () => {
                            try {
                                const elemento = document.getElementById('btn-toggle-profile');
                                if (elemento && !elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }
                        }
                    },
                    {
                        element: "#btn-toggle-profile",
                        title: "Menu do usuário",
                        content: "<p>Links rápidos, trocar para o tema anterior, alterar preferências e sair. Está tudo aqui, pensado em você!</p>",
                        placement: "top-start",
                        onPrevious: () => {
                            try {
                                const elemento = document.getElementById('btn-toggle-help');
                                if (elemento && !elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }
                        },
                        onNext: () => {
                            localStorage.setItem("completou-user-tour01", true);
                            try {
                                const elemento = document.getElementById('btn-toggle-profile');
                                if (elemento && elemento.classList.contains('active')) {
                                    elemento.click();
                                }
                            } catch (e) {
                                console.error('Erro ao clicar no elemento:', e);
                            }                            
                        },
                    },
                ];
                if (this.diarios.length > 0) {
                    steps.splice(1, 0, {
                        element: ".text-decoration-none",
                        title: "Sua sala de aula",
                        content: "<p>Você pode acessar suas salas clicando no <b>nome da sala ou no identificador</b> da sala.</p>" +
                                "<p>Aprenda nos próximos passos como usar os filtros para encontrar salas específicas, passadas, planejadas ou favoritas.</p>",
                        placement: "bottom-start",
                    });
                    steps.splice(2, 0, {
                        element: ".painel-card-details-info-unfavourite, .painel-card-details-info-favourite",
                        title: "Favorite uma sala",
                        content: "<p>Você tem muitas salas? Favorite as que você vai estudar mais neste semestre, então acesse elas <b>filtrando pelas favoritas<b>.",
                        placement: "bottom-end",
                    });
                }
                try {
                    const wt = new WebTour();
                    wt.setSteps(steps);
                    wt.start();
                } catch (e) {
                    console.error('Erro ao adicionar passos do tour:', e);
                }
            }
        }
    }
});

// Iniciar o app Vue após o carregamento do DOM
document.addEventListener('DOMContentLoaded', () => {
    try {
        app.mount('#app');
        console.log('Aplicação Vue montada com sucesso');
    } catch (e) {
        console.error('Erro ao montar a aplicação Vue:', e);
    }
});