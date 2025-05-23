import logging

from sqlalchemy import String, Enum, Float, Boolean, Integer, DateTime

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
            logging.info(f"Registro salvo com sucesso: {new_instance}")

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

            value = None if self.instance is None else getattr(self.instance, field.name)
            new_value = None


            if bool(field.foreign_keys):
                #pega todos os items da tabela relacionada e exibe um selectbox

                # Obter o nome da tabela relacionada
                table_name = list(field.foreign_keys)[0].column.table.name

                # Importar dinamicamente o modelo relacionado
                related_class = get_model_by_table_name(table_name)

                # Buscar todos os registros da tabela relacionada
                related_items = related_class.all()

                # Criar opções para o selectbox
                options = [(item.id, str(item)) for item in related_items]

                # Obter o valor atual
                current_value = value if value else None

                # Exibir o selectbox
                new_value = st.selectbox(
                    label=self.model.get_field_display_name(field.name),
                    options=options,
                    format_func=lambda x: x[1],
                    index=[opt[0] for opt in options].index(current_value) if current_value else None,
                    help=field.comment,
                )

                if new_value is not None:
                    data[field.name] = new_value[0]
                else:
                    data[field.name] = None

            elif isinstance(field.type, Enum):

                options = [item.value for item in field.type.enum_class]

                index = options.index(value) if value in options else None

                new_value = st.selectbox(
                    index=index,
                    options=options,
                    format_func=lambda x: str(field.type.enum_class(x)),
                    label=self.model.get_field_display_name(field.name),
                    help=field.comment,
                    placeholder="Escolha uma opção",

                )

                data[field.name] = new_value

            elif isinstance(field.type, Float):
                # Exibir um campo de texto para editar o valor
                new_value = st.number_input(
                    value=value,
                    label=self.model.get_field_display_name(field.name),
                    help=field.comment,
                    format="%.2f",
                    step=0.01,
                )

                data[field.name] = new_value

            elif isinstance(field.type, Integer):
                # Exibir um campo de texto para editar o valor
                new_value = st.number_input(
                    value=value,
                    label=self.model.get_field_display_name(field.name),
                    help=field.comment,
                    format="%d",
                    step=1,
                )

                data[field.name] = new_value

            elif isinstance(field.type, Boolean):

                if field.nullable:
                    options = ["Sim", "Não", "Indefinido"]
                else:
                    options = ["Sim", "Não"]

                _valor = "Sim" if value else "Não" if value is not None else "Indefinido"

                index = options.index(_valor) if _valor in options else None

                new_value = st.selectbox(
                    label=self.model.get_field_display_name(field.name),
                    options=options,
                    index=index,
                    help=field.comment,
                )

                data[field.name] = True if new_value == "Sim" else False

            elif isinstance(field.type, String):
                # Exibir um campo de texto para editar o valor
                new_value = st.text_input(
                    value=value,
                    label=self.model.get_field_display_name(field.name),
                    help=field.comment,
                    max_chars=field.type.length,
                )

                data[field.name] = new_value

            elif isinstance(field.type, DateTime):
                # Exibir um campo de data/hora para editar o valor
                date = st.date_input(
                    label=f"{self.model.get_field_display_name(field.name)} - Data",
                    format="DD/MM/YYYY",
                    value=value,
                    help=field.comment,
                )

                time = st.time_input(
                    label=f"{self.model.get_field_display_name(field.name)} - Hora",
                    value=value,
                    help=field.comment,
                )

                if date is not None or time is not None:

                    dateTimeValue = datetime.combine(date or datetime.now().date(), time or datetime.now().time())

                    data[field.name] = dateTimeValue
                else:
                    data[field.name] = None

            else:
                logging.warning(f"Tipo de campo não suportado: {field.type}")
                st.warning(f"Tipo de campo não suportado: {field.type}")
                raise NotImplementedError(f"Tipo de campo não suportado: {field.type}")

            if self.can_show_validation() and self.model.validate_field(field.name, new_value):
                st.warning(f"Valor inválido para o campo {self.model.get_field_display_name(field.name)}: {self.model.validate_field(field.name, new_value)}")

        return data

