import * as VueSelect from './vue-select.js';

const app = Vue.createApp({
    components: {
        'v-select': VueSelect.default,
    },
    data() {
        return {
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
            tabs: ['Meus Diários', 'Salas de Coordenação', 'Práticas', 'Reutilizar'],
            // selectedDisciplina: null,
            // selectedSemestre: null,
            // selectedSituacao: 'inprogress',
            // selectedCurso: null,
            // selectedAmbiente: null,
            // selectedPeriodo: null,
            // selectedModulo: null,
            filters: {
                situacao: 'inprogress', // Valor inicial obrigatório
                semestre: null,
                periodo: null,
                modulo: null,
                disciplina: null,
                curso: null,
                ambiente: null
            },


            searchItems: [
                { id: 1, name: 'Item 1' },
                { id: 2, name: 'Item 2' },
                { id: 3, name: 'Item 3' },
                { id: 4, name: 'Item 4' },
                { id: 5, name: 'Item 5' },
            ],
            list1: [
                { id: 1, name: 'Item 1', description: 'Descrição do item 1' },
                { id: 2, name: 'Item 2', description: 'Descrição do item 2' },
                { id: 3, name: 'Item 3', description: 'Descrição do item 3' },
                { id: 4, name: 'Item 4', description: 'Descrição do item 4' },
                { id: 5, name: 'Item 5', description: 'Descrição do item 5' },
                { id: 6, name: 'Item 6', description: 'Descrição do item 6' },
                { id: 7, name: 'Item 7', description: 'Descrição do item 7' },
                { id: 8, name: 'Item 8', description: 'Descrição do item 8' },
                { id: 9, name: 'Item 9', description: 'Descrição do item 9' },
                { id: 10, name: 'Item 10', description: 'Descrição do item 10' }
            ],
            list2: [
                { id: 1, name: 'Item 1', value: 100 },
                { id: 2, name: 'Item 2', value: 200 },
                { id: 3, name: 'Item 3', value: 300 }
            ],
            list3: [
                { id: 1, name: 'Item 1', status: 'Ativo' },
                { id: 2, name: 'Item 2', status: 'Inativo' },
                { id: 3, name: 'Item 3', status: 'Pendente' }
            ],
            list4: [
                { id: 1, name: 'Item 1', date: '2023-01-01' },
                { id: 2, name: 'Item 2', date: '2023-02-15' },
                { id: 3, name: 'Item 3', date: '2023-03-30' }
            ],

            splideInstance: null,
            selectedMessageOption: 'all',
            messageOptions: [
                { label: 'Todos', value: 'all' },
                { label: 'Não lidas', value: 'unread' },
                { label: 'Grupos', value: 'groups' },
                { label: 'Favoritos', value: 'favorites' },
                { label: 'Privado', value: 'private' }
            ],
            messages: [
                { id: 1, receiver: 'Ronaldo', sender: '', content: 'Conteúdo da mensagem 1', date: '2023-03-25 12:00', read: false, favorite: true, group: '', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8E7wlGmOb1_0GI4vqlvieVWlGdkMW5Mv0XQ&s' },
                { id: 2, receiver: '', sender: 'Messi', content: 'Conteúdo da mensagem 22222222222222222222222222222222222222222222222222', date: '2023-01-02 14:00', read: true, favorite: true, group: 'Grupo A', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxLoJONSCCuN_JBwM_xVD5hloPBf4pHB9R7A&s' },
                { id: 3, receiver: 'Neymar', sender: '', content: 'Conteúdo da mensagem 3', date: '2023-01-03 16:00', read: false, favorite: false, group: 'Grupo B', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNMnJ3i8BARfyzD9fxQ9GvorEDF1gTrZqzrA&s' },
                { id: 4, receiver: '', sender: 'Cristiano Ronaldo', content: 'Conteúdo da mensagem 44444444444444', date: '2023-01-04 18:00', read: true, favorite: true, group: '', img: 'https://img.a.transfermarkt.technology/portrait/big/8198-1694609670.jpg?lm=1' },
                { id: 5, receiver: 'Zidane', sender: '', content: 'Conteúdo da mensagem 5', date: '2023-03-25 20:00', read: false, favorite: false, group: 'Grupo A', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoSDG52Efy_SkQKqp9tTaS46NaaZCNEX2LJQ&s' },
                { id: 6, receiver: 'Ronaldinho', sender: '', content: 'Conteúdo da mensagem 6666666666666', date: '2023-03-25 12:00', read: true, favorite: true, group: 'Grupo A', img: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSioEdBrFFM0iW0f6uhegsUMeMptl48GSdOeQ&s' },
            ],
            messageSearchQuery: '',
            notifications: [
                { id: 1, title: 'Notificação 1', date: '2025-03-25 12:00', link: '#' },
                { id: 2, title: 'Notificação 2', date: '2025-01-02 14:00', link: '#' },
                { id: 3, title: 'Notificação 3', date: '2025-01-03 16:00', link: '#' },
                { id: 4, title: 'Notificação 4', date: '2025-01-04 18:00', link: '#' },
                { id: 5, title: 'Notificação 5', date: '2025-03-25 20:00', link: '#' },
                { id: 6, title: 'Notificação 6', date: '2025-03-21 12:00', link: '#' },
                { id: 7, title: 'Notificação 9', date: '2025-03-25 12:00', link: '#' },
                // { id: 8, title: 'Notificação 11', date: '2025-03-18 12:00', link: '#' },
                // { id: 9, title: 'Notificação 12', date: '2025-03-18 12:00', link: '#' },
                // { id: 10, title: 'Notificação 13', date: '2025-03-25 12:00', link: '#' },
                // { id: 11, title: 'Notificação 15', date: '2025-03-02 12:00', link: '#' },
                // { id: 12, title: 'Notificação 16', date: '2025-03-27 14:00', link: '#' },
                // { id: 13, title: 'Notificação 17', date: '2025-03-27 09:00', link: '#' },
                // { id: 14, title: 'Notificação 18', date: '2025-02-25 09:00', link: '#' },
                // { id: 15, title: 'Notificação 20', date: '2025-03-27 12:00', link: '#' },
            ],
            filterSearchQuery: '',
            periodos: [
                { label: "2023/1", id: "20231" },
                { label: "2023/2", id: "20232" },
                { label: "2024/1", id: "20241" },
                { label: "2024/2", id: "20242" },
                { label: "2025/1", id: "20251" },
                { label: "2025/2", id: "20252" },
            ],
            modulos: [
                { label: "1º Módulo", id: "1" },
                { label: "2º Módulo", id: "2" },
                { label: "3º Módulo", id: "3" },
                { label: "4º Módulo", id: "4" },
                { label: "5º Módulo", id: "5" },
                { label: "6º Módulo", id: "6" },
                { label: "7º Módulo", id: "7" },
                { label: "8º Módulo", id: "8" },
            ],
            semestres: [
                { label: "1º Semestre", id: "1" },
                { label: "2º Semestre", id: "2" },
                { label: "3º Semestre", id: "3" },
                { label: "4º Semestreeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", id: "4" },
                { label: "5º Semestre", id: "5" },
                { label: "6º Semestre", id: "6" },
                { label: "7º Semestre", id: "7" },
                { label: "8º Semestre", id: "8" },
            ],
            situacoes: [
                { label: "Diários em andamento", id: "inprogress" },
                { label: "Diários a iniciar", id: "future" },
                { label: "Encerrados pelo professor", id: "past" },
                { label: "Meus diários favoritosssssssssssssssssssss", id: "favourites" },
                { label: "Todos os diários (lento)", id: "allincludinghidden" },
            ],
            disciplinas: [
                { id: 1, label: 'Matemática' },
                { id: 2, label: 'Português' },
                { id: 3, label: 'História' },
                { id: 4, label: 'Geografia' },
                { id: 5, label: 'Ciências' },
                { id: 6, label: 'Educação Física' },
                { id: 7, label: 'Artes' },
                { id: 8, label: 'Inglês' },
                { id: 9, label: 'Física' },
                { id: 10, label: 'Química' }
            ],
            cursos: [
                { id: 1, label: 'Curso 1' },
                { id: 2, label: 'Curso 2' },
                { id: 3, label: 'Curso 3' },
                { id: 4, label: 'Curso 4' },
                { id: 5, label: 'Curso 5' },
                { id: 6, label: 'Curso 6' },
                { id: 7, label: 'Curso 7' },
                { id: 8, label: 'Curso 8' },
            ],
            ambientes: [
                { id: 1, label: 'Ambiente 1' },
                { id: 2, label: 'Ambiente 2' },
                { id: 3, label: 'Ambiente 3' },
                { id: 4, label: 'Ambiente 4' },
                { id: 5, label: 'Ambiente 5' },
                { id: 6, label: 'Ambiente 6' },
                { id: 7, label: 'Ambiente 7' },
                { id: 8, label: 'Ambiente 8' },
            ],
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
        }
    },
    computed: {
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
        this.filterCards();
    },
    methods: {
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

            console.log('messageDate:', messageDate.toDateString());
            console.log('today:', today.toDateString());
            
            
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
            console.log(value);
            
            this.selectedMessageOption = value;  
            if (this.splideInstance) {
                this.splideInstance.refresh();
            }
        },
        openModalWithContent(type) {
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
            this.sidebarContracted = !this.sidebarContracted
        },
        toggleSidebarModal() {
            this.modalOpen = !this.modalOpen;
            this.modalType = '';
            this.modalTitle = '';
            this.modalHeaderIcon = '';
        },
        setActiveTab(index) {
            this.activeTab = index;
        },
        filterCards() {
            console.log("Filtering cards...");
            
            try {
                const params = new URLSearchParams({
                    q: this.q || localStorage.q || "",
                    situacao: this.situacao || localStorage.situacao || "inprogress",
                    semestre: this.semestre || localStorage.semestre || "",
                    disciplina: this.disciplina || localStorage.disciplina || "",
                    curso: this.curso || localStorage.curso || "",
                    ambiente: this.ambiente || localStorage.ambiente || "",
                });

                fetch(`http://painel/api/v1/diarios/?${params.toString()}`)
                    .then((response) => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then((data) => {
                        console.log("Response:", data);
                    })
                    .catch((error) => {
                        console.error("Error fetching data:", error);
                    });
            } catch (e) {
                console.debug(e);
            }
        },
        // removeFilter(type) {
        //     console.log("Removing filter:", type);
        //     switch (type) {
        //         case 'situacao':
        //             this.selectedSituacao = null;
        //             break;
        //         case 'semestre':
        //             this.selectedSemestre = null;
        //             break;
        //         case 'disciplina':
        //             this.selectedDisciplina = null;
        //             break;
        //         case 'curso':
        //             this.selectedCurso = null;
        //             break;
        //         case 'ambiente':
        //             this.selectedAmbiente = null;
        //             break;
        //         default:
        //             break;
        //     }
        // },
        removeFilter(filterType) {
            if (filterType === 'situacao') return; // Impede remoção do filtro padrão
            this.filters[filterType] = null;
            this.filterCards(); // Atualiza os resultados
        },
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