import streamlit as st
from sqlalchemy import BinaryExpression

from src.dashboard.generic.edit_view import EditView
from src.dashboard.generic.model_query_filters import ModelQueryFilters
from src.dashboard.generic.simple_plots import SimplePlotView
from src.database.tipos_base.model import Model
from math import ceil


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

    def get_plot_page(self) -> st.Page:
        """
        Retorna a página de plotagem genérica do modelo.
        :return: st.Page - A página para plotagem do modelo.
        """
        if self.model.__generic_plot__ is None:
            raise NotImplementedError(
                "A classe não implementa o método 'get_plot_page' ou não possui um 'generic_plot' definido.")

        plot_view = SimplePlotView(self.model)

        return st.Page(
                plot_view.view,
                title=f"{self.model.display_name_plural()} - Gráfico",
                url_path=f"{self.model.__name__.lower()}-grafico"
            )

    def redirect_to_plot_page(self):
        """
        Redireciona para a página de plotagem do modelo.
        :return: None
        """
        st.switch_page(self.get_plot_page())

    def get_routes(self) -> list:

        rotas = [
            self.get_table_page(),
            # self.get_edit_page(),
        ]

        if self.model.__generic_plot__ is not None:
            rotas.append(self.get_plot_page())

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

        if self.model.__table_view_filters__ is not None:
            col0, col1, col2 = st.columns([1, 5, 1])
        else:
            col0 = None
            col1, col2 = st.columns([5, 1])

        model_filters = ModelQueryFilters(self.model)

        if col0:
            with col0:
                model_filters.render()


        selected = {'selection': {'rows': [], 'columns': []}}

        filters_valid:list[BinaryExpression] = []
        offset = st.query_params.get('offset', None)

        for f in model_filters.get_filters():
            if f.value is not None or f.optional == False:
                filters_valid.append(f.get_sqlalchemy_filter(self.model, model_filters.get_correct_filter_value(f)))

        dataframe = self.model.filter_dataframe(
            select_fields=self.model.__table_view_fields__,
            filters=None if not filters_valid else filters_valid,
            order_by=[self.model.id.desc()] if self.model.id is not None else None,
            limit=self.model.__table_view_itens_per_page__,
            offset=offset,
            as_display=True
        )

        with col1:

            selected = st.dataframe(dataframe,
                         on_select="rerun",
                         selection_mode="single-row",
                         key="id",
                         hide_index=True,
                         )

            self.paginacao(filters_valid)

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

            if self.model.__generic_plot__ is not None:
                if st.button("Gráfico"):
                    self.redirect_to_plot_page()
                    st.rerun()


    def paginacao(self, filters: list[BinaryExpression] = None):

        total_itens = self.model.count(filters=filters)

        if total_itens < self.model.__table_view_itens_per_page__:
            return

        total_paginas = ceil(total_itens / self.model.__table_view_itens_per_page__)
        coluna_paginas, coluna_botao = st.columns([4, 1])

        pagina_atual = ceil(int(st.query_params.get('offset', 0)) / self.model.__table_view_itens_per_page__) + 1

        if pagina_atual > total_paginas:
            st.query_params.pop('offset', None)
            st.rerun()

        with coluna_paginas:

            st.write(f"Página {pagina_atual} de {total_paginas}")

        with coluna_botao:
            def mudar_pagina(page: int):
                """
                Função para mudar a página da tabela.
                :param page: Página para a qual mudar.
                """

                offset_value = (page - 1) * self.model.__table_view_itens_per_page__

                if offset_value != st.query_params.get('offset', 0):
                    st.query_params['offset'] = offset_value
                    st.rerun()

            nova_pagina = st.number_input(
                "Página",
                min_value=1,
                max_value=total_paginas,
                value=pagina_atual,
                step=1,
            )

            if nova_pagina != pagina_atual:
                mudar_pagina(nova_pagina)


    def edit_view(self, model_id: int|None = None):
        """
        Função para exibir o formulário de edição.
        :param model_id:
        :return:
        """
        edit_instance = EditView(self.model, model_id)
        return edit_instance.get_cadastro_view()