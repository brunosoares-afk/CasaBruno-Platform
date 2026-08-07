import { createTheme } from "@mui/material/styles";

const theme = createTheme({

    palette: {

        mode: "dark",

        primary: {

            main: "#1565FF"

        },

        secondary: {

            main: "#FF4FD8"

        },

        background: {

            default: "#08111F",

            paper: "#10233F"

        },

        success: {

            main: "#00C853"

        },

        warning: {

            main: "#FFB300"

        },

        error: {

            main: "#F44336"

        },

        info: {

            main: "#29B6F6"

        },

        text: {

            primary: "#FFFFFF",

            secondary: "#B6C2CF"

        }

    },

    typography: {

        fontFamily: [

            "Inter",

            "Roboto",

            "Arial",

            "sans-serif"

        ].join(","),

        h3: {

            fontWeight: 700

        },

        h4: {

            fontWeight: 700

        },

        h5: {

            fontWeight: 700

        },

        h6: {

            fontWeight: 600

        },

        subtitle1: {

            fontWeight: 500

        },

        button: {

            textTransform: "none",

            fontWeight: 600

        }

    },

    shape: {

        borderRadius: 18

    },

    components: {

        MuiPaper: {

            styleOverrides: {

                root: {

                    backgroundImage: "none"

                }

            }

        },

        MuiCard: {

            styleOverrides: {

                root: {

                    background: "rgba(16,35,63,.78)",

                    border: "1px solid rgba(255,255,255,.05)",

                    backdropFilter: "blur(18px)",

                    boxShadow: "0 10px 30px rgba(0,0,0,.35)"

                }

            }

        },

        MuiButton: {

            styleOverrides: {

                root: {

                    borderRadius: 14,

                    paddingLeft: 18,

                    paddingRight: 18

                }

            }

        }

    }

});

export default theme;
