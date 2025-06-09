import logging

from sqlalchemy import String, Enum, Float, Boolean, Integer, DateTime

from src.dashboard.generic.model_form_fields import ModelFormField
from src.dashboard.global_messages import add_global_message
from src.database.dynamic_import import import_models, get_model_by_table_name
from src.database.tipos_base.model import Model
import streamlit as st
from datetime import datetime

@st.dialog("Confirmar Exclusão")
def comfirmar_exclusao(messagem: str):
    """
    Função para confirmar a exclusão de um registro.
    :param messagem: str - Mensagem a ser exibida na confirmação.
    :return: bool - True se o usuário confirmar a exclusão, False caso contrário.
    """
    st.write(messagem)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Não"):
            st.session_state['confirmar_exclusao'] = False
            st.rerun()

    with col2:
        if st.button("Sim"):
            st.session_state['confirmar_exclusao'] = True
            st.rerun()



class EditView:
    """
    EditView is a class that provides functionality to edit a dashboard.
    It includes methods to load the dashboard, edit its properties, and save changes.
    """

    def __init__(self, model: type[Model], model_id: int|None=None, instance: Model|None=None):
        self.model = model
        self.model_id = model_id
        self.instance = instance

        if model_id is not None and instance is None:
            self.instance = model.get_from_id(model_id)
        elif instance is not None:
            self.instance = instance
            self.id = instance.id

    def show_validation(self, show:bool=True):
        """
        Função para exibir ou ocultar o formulário de validação.
        :param show: bool - Se True, exibe o formulário de validação.
        :return:
        """
        if show:
            st.session_state[f"{self.model.__name__}__error__"] = True
        else:
            st.session_state[f"{self.model.__name__}__error__"] = False

    def can_show_validation(self) -> bool:
        """
        Função para verificar se o formulário de validação pode ser exibido.
        :return: bool - Se True, o formulário de validação pode ser exibido.
        """
        return st.session_state.get(f"{self.model.__name__}__error__", False)

    def get_cadastro_view(self):
        """
        Função para exibir o formulário de cadastro.
        :return:
        """
        st.title(self.model.display_name())

        # criar colunas
        col1, col2 = st.columns([3, 1])

        with col1:
            data = self.get_fields()

        with col2:
            # Criar um novo registro
            if st.button("Salvar"):
                if self.model.is_valid(data):
                    self.show_validation(False)
                    self.save(data)
                else:
                    logging.warning(f"Dados inválidos para {self.model.display_name()}. Verifique os campos e tente novamente.")
                    self.show_validation(True)
                    st.rerun()
            if self.model_id is not None:
                # Excluir o registro atual
                if st.button("Excluir") or st.session_state.get("confirmar_exclusao") is not None:

                    if st.session_state.get("confirmar_exclusao") is None:
                        comfirmar_exclusao(f"Você tem certeza que deseja excluir o registro {self.instance.id}?")

                    elif st.session_state.get("confirmar_exclusao") == False:
                        st.session_state["confirmar_exclusao"] = None

                    elif st.session_state.get("confirmar_exclusao") == True:
                        st.session_state["confirmar_exclusao"] = None
                        self.instance.delete()
                        add_global_message(f"Exclusão do registro {self.model_id} efetuada com sucesso")
                        logging.info(f"Exclusão do registro {self.model_id} efetuada com sucesso")

                        if st.query_params.get('id') is not None:
                            st.query_params.pop('id')

                        if st.query_params.get('edit') is not None:
                            st.query_params.pop('edit')

                        st.rerun()

                    else:
                        raise NotImplementedError("Erro ao excluir o registro")



    def save(self, data: dict):
        '''
        Função para salvar os dados do formulário no banco de dados.
        :param data: dict - Dados do formulário.
        :return:
        '''

        try:

            if self.instance is None:

                new_instance = self.model.from_dict(data)
            else:
                new_instance = self.instance.update_from_dict(data)

            # Salvar a nova instância no banco de dados
            new_instance.save()

            add_global_message("Registro salvo com sucesso!")

            if st.query_params.get('id') is not None:
                st.query_params.pop('id')

            if st.query_params.get('edit') is not None:
                st.query_params.pop('edit')

            st.rerun()

        except Exception as e:
            logging.error(f"Erro ao salvar o registro: {e}")
            st.error(f"Erro ao salvar o registro. Verifique os dados e tente novamente.\n{e}")
            raise

    def delete(self):
        """
        Função para excluir o registro atual.
        :return:
        """
        if self.instance is not None:
            self.instance.delete()
            st.success(f"Registro {self.instance.id} excluído com sucesso!")
            logging.info(f"Registro excluído com sucesso: {self.instance}")
            st.rerun()
        else:
            st.warning("Nenhum registro selecionado para exclusão.")


    def get_fields(self) -> dict:
        """
        Função para exibir os campos do formulário.
        :return:
        """

        data = {}

        for field in self.model.fields():
            if field.name == 'id':
                logging.debug('Campo id não editável, skipping...')
                continue

            initial_value = None if self.instance is None else getattr(self.instance, field.name)

            form_field = ModelFormField(self.model, field_name=field.name)

            new_value = form_field.render(initial_value=initial_value, show_validation=self.can_show_validation())

            if new_value is not None:
                data[field.name] = new_value
            else:
                data[field.name] = None

        return data

