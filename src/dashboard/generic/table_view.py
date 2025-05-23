import streamlit as st
from src.dashboard.generic.edit_view import EditView
from src.database.tipos_base.model import Model


class TableView:
    """
    View que exibe uma tabela de um modelo e permite a edição dos registros.
    """

    def __init__(self, model: type[Model]):
        self.model = model

    def get_table_page(self) -> st.Page:
        return st.Page(
                self.manage_routes,
                title=self.model.display_name_plural(),
                url_path=self.model.__name__.lower()
            )

    #tive que excluir o get_edit_page porque o Streamlit não permite criar rotas dinamicamente
    # def get_edit_page(self, instance_id = None) -> st.Page:
    #     page = st.Page(
    #             self.edit_view,
    #             title=f"Editar {self.model.display_name()}" if instance_id is not None else f"Criar {self.model.display_name()}",
    #             # De acordo com a documentação do Streamlit, o url_path não pode ter /
    #             url_path=f"{self.model.__name__.lower()}_edit",
    #         )
    #
    #     return page

    def get_routes(self) -> list:

        rotas = [
            self.get_table_page(),
            # self.get_edit_page(),
        ]

        return rotas

    def manage_routes(self):
        """
        Função para gerenciar as rotas da view.
        Necessário porque o Streamlit não permite criar rotas dinamicamente.
        Com tentativa e erro cheguei a conclusão que a melhor forma é manipular os query params.
        :return:
        """
        if st.query_params.get('edit') is None:
            return self.table_view()

        else:
            model_id = st.query_params.get('id')
            return self.edit_view(model_id)


    def table_view(self):

        st.title(self.model.display_name_plural())

        col1, col2 = st.columns([5, 1])

        selected = {'selection': {'rows': [], 'columns': []}}
        dataframe = self.model.as_dataframe_display()

        with col1:

            selected = st.dataframe(dataframe,
                         on_select="rerun",
                         selection_mode="single-row",
                         key="id",
                         hide_index=True,
                         )

        with (col2):
            if st.button("Novo"):

                if st.query_params.get('id') is not None:
                    st.query_params.pop('id')

                st.query_params['edit'] = 1
                st.rerun()

            if st.button("Editar",
                    disabled=selected.get("selection", {}).get("rows", []) == []
                         ):
                selected_row = selected["selection"]["rows"][0]
                row_id = dataframe.loc[selected_row, self.model.get_field_display_name('id')]
                st.query_params['id'] = row_id
                st.query_params['edit'] = 1
                st.rerun()

    def edit_view(self, model_id: int|None = None):
        """
        Função para exibir o formulário de edição.
        :param model_id:
        :return:
        """
        edit_instance = EditView(self.model, model_id)
        return edit_instance.get_cadastro_view()