export default {
    compilerOptions: {
        delimiters: ["[[", "]]"]
    },
    data() {
        return {
        }
    },

    mounted() {
        $('#app').css('display', 'block');
        $('#pre-loading').css('display', 'none');
    },
    methods: {

        toggleNavBar(e) {
            if (e) {
                e.preventDefault();
            }
            if (localStorage.contentClosed == 'true') {
                $('.filter-wrapper').removeClass('closed');
                localStorage.contentClosed = 'false'
            } else {
                $('.filter-wrapper').addClass('closed');
                localStorage.contentClosed = 'true'
            }
        },

    },

}
