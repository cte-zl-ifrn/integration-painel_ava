export default {
    compilerOptions: {
        delimiters: ["[[", "]]"],
    },
    data() {
        return {
            atualizacoes: [],
            unread_notification_total:0,
            unread_conversations_total:0,
        };
    },
    mounted() {
        this.showAtualizacoes();
    },
    methods: {
        showAtualizacoes: function () {
            $(".icon-count").css("display", "inline-block");
            // axios.get("/api/v1/atualizacoes_counts/", { params: {} }).then((response) => {
            //     Object.assign(this, response.data);
            //     //console.log('PRINT:',response.data)
            // });
        },
    },
};
