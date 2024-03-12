from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, Sum
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import *
from .serializers import *
from datetime import timedelta
import difflib, re, imghdr

# Create your views here.
class UsuarioView(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses = {
            201: 'Usuario creado exitosamente.',
            400: 'La solicitud contiene datos incorrectos o incompletos.',
            500: 'Se ha producido un error en el servidor.'
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo usuario

        Para crear un nuevo usuario, se deben proporcionar los siguientes campos en formato JSON:
        - 'nombre': El nombre del usuario. Debe tener una longitud de hasta 50 caracteres y no puede estar vacío.
        - 'correo': La dirección de correo electrónico del usuario. Debe tener una longitud de hasta 254 caracteres, no puede estar vacía y debe ser única en la base de datos.
        - 'password': La contraseña del usuario. Debe tener una longitud de entre 8 y 12 caracteres, contener al menos un carácter especial y no puede estar vacía. Además, la contraseña no puede coincidir con el nombre ni con el correo electrónico del usuario.
        """
        nombre = request.data['nombre'].strip()
        correo = request.data['correo'].strip()
        password = request.data['password'].strip()
        mensaje = {}
        datos_validados = True

        if len(nombre) < 1 or len(nombre) > 50:
            mensaje['nombre'] = 'Por favor, ingrese un nombre válido con un máximo de 50 caracteres'
            datos_validados = False
        
        if not correo:
            mensaje['correo'] = 'Por favor, asegúrate de ingresar tu correo electrónico. Este campo no puede estar vacío'
            datos_validados = False
        elif len(correo) > 254:
            mensaje['correo'] = 'Por favor, ingrese un correo válido con un máximo de 254 caracteres'
            datos_validados = False
        elif Usuario.objects.filter(correo = correo).exists():
            if Usuario.objects.filter(correo = correo, estado = True).exists():
                mensaje['correo'] = 'Por favor selecciona otro correo electrónico, debido a que ya existe una cuenta asociada a este correo'
                datos_validados = False
            elif Usuario.objects.filter(correo = correo, estado = False).exists():
                Usuario.objects.get(correo = correo, estado = False).delete()
        else:
            try:
                validate_email(correo)
            except ValidationError as e:
                mensaje['correo'] = 'Por favor, verifica que esté escrito correctamente debido a que has ingresado uno no válido'
                datos_validados = False

        patron = r'[!@#$%^&*()\-_=+{};:,<.>/?[\]\'"`~\\|]'
        similitud_1 = difflib.SequenceMatcher(None, nombre.lower(), password.lower()).ratio()
        similitud_2 = difflib.SequenceMatcher(None, correo.lower(), password.lower()).ratio() 
        if not password:
            mensaje['password'] = 'Por favor, asegúrate de ingresar tu contraseña. Este campo no puede estar vacío'
            datos_validados = False
        elif len(password) < 8 or len(password) > 12:
            mensaje['password'] = 'Por favor, ingresa una contraseña con un mínimo de 8 caracteres y un máximo de 12 caracteres'
            datos_validados = False
        elif not re.search(patron, password):
            mensaje['password'] = 'Por favor, asegúrate de incluir al menos un carácter especial en tu contraseña'
            datos_validados = False
        elif similitud_1 > 0.4 and similitud_2 > 0.4:
            mensaje['password'] = 'Por favor, elige una contraseña que no contenga información personal'
            datos_validados = False
        
        request.data['password'] = make_password(password)
        serializer = self.get_serializer(data = request.data)
        try:
            serializer.is_valid()
            if datos_validados:
                usuario = serializer.save()
                token = UsuarioToken.objects.get(idUsuario = usuario.id)
                serializerToken = UsuarioTokenSerializer(token)
                return Response({
                    'estado': 201,
                    'validar': True,
                    'mensaje': '¡Registro completado! Revisa tu bandeja de entrada para confirmar tu cuenta. No olvides verificar la carpeta de spam si no encuentras el correo en tu bandeja principal',
                    'datos': serializerToken.data
                }, status = status.HTTP_201_CREATED)
            else:
                return http_400_error(mensaje)
        except Exception as e:
            return Response({
                'estado': 500,
                'validar': False,
                'mensaje': {
                    'serializador': serializer.errors,
                    'Excepciones': str(e)
                }
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        responses = {
            200: 'Usuario actualizado correctamente.',
            400: 'La solicitud contiene datos incorrectos o incompletos.',
            500: 'Se ha producido un error en el servidor.'
        }
    )        
    def update(self, request, *args, **kwargs):
        """
        Actualizar un usuario existente

        Para actualizar un usuario, se deben proporcionar los siguientes campos:
        - 'id': El ID único del usuario que se desea actualizar. Debe coincidir con el ID del usuario que se desea modificar.
        - 'foto': La foto del usuario en formato JPEG o PNG, codificada en base64. Este campo no puede estar vacío.
        - 'nombre': El nombre del usuario. Debe tener una longitud máxima de 50 caracteres y no puede estar vacío.
        - 'correo': La dirección de correo electrónico del usuario. Debe tener una longitud máxima de 254 caracteres, no puede estar vacía y debe ser única en la base de datos.
        - 'password': La nueva contraseña del usuario. Debe tener una longitud de entre 8 y 12 caracteres, contener al menos un carácter especial y no puede estar vacía. Además, la contraseña no puede coincidir con el nombre ni con el correo electrónico del usuario.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        nombre = request.data['nombre'].strip()
        correo = request.data['correo'].strip()
        password = request.data['password'].strip()
        mensaje = {}
        datos_validados = True

        try:
            foto = request.data['foto']
            if not imghdr.what(foto) or imghdr.what(foto) not in ['jpeg', 'png']:
                mensaje['foto'] = 'Por favor, asegúrate de cargar una imagen en formato JPG o PNG para completar el proceso'
                datos_validados = False
        except Exception as e:
            mensaje['foto'] = 'Por favor, asegúrate de ingresar tu foto de perfil. Este campo no puede estar vacío'
            # datos_validados = False
            
        if len(nombre) < 1 or len(nombre) > 50:
            mensaje['nombre'] = 'Por favor, ingrese un nombre válido con un máximo de 50 caracteres'
            datos_validados = False
        
        if not correo:
            mensaje['correo'] = 'Por favor, asegúrate de ingresar tu correo electrónico. Este campo no puede estar vacío'
            datos_validados = False
        elif len(correo) > 254:
            mensaje['correo'] = 'Por favor, ingrese un correo válido con un máximo de 254 caracteres'
            datos_validados = False
        elif Usuario.objects.filter(~Q(id = instance.id), correo = correo, estado = True).exists():
            mensaje['correo'] = 'Por favor selecciona otro correo electrónico, debido a que ya existe una cuenta asociada a este correo'
            datos_validados = False

        patron = r'[!@#$%^&*()\-_=+{};:,<.>/?[\]\'"`~\\|]'
        similitud_1 = difflib.SequenceMatcher(None, nombre.lower(), password.lower()).ratio()
        similitud_2 = difflib.SequenceMatcher(None, correo.lower(), password.lower()).ratio() 
        if not password:
            mensaje['password'] = 'Por favor, asegúrate de ingresar tu contraseña. Este campo no puede estar vacío'
            datos_validados = False
        elif len(password) < 8 or len(password) > 12:
            mensaje['password'] = 'Por favor, ingresa una contraseña con un mínimo de 8 caracteres y un máximo de 12 caracteres'
            datos_validados = False
        elif not re.search(patron, password):
            mensaje['password'] = 'Por favor, asegúrate de incluir al menos un carácter especial en tu contraseña'
            datos_validados = False
        elif similitud_1 > 0.4 and similitud_2 > 0.4:
            mensaje['password'] = 'Por favor, elige una contraseña que no contenga información personal'
            datos_validados = False

        request.data['password'] = make_password(password)
        serializer = self.get_serializer(instance, data = request.data, partial = partial)
        try:
            serializer.is_valid()
            if datos_validados:
                serializer.save()
                return Response({
                    'estado': 200,
                    'validar': True,
                    'mensaje': 'La información se ha actualizado con éxito',
                    'datos': serializer.data
                }, status = status.HTTP_200_OK)
            else:
                return http_400_error(mensaje)
        except Exception as e:
            return Response({
                'estado': 500,
                'validar': False,
                'mensaje': {
                    'serializador': serializer.errors,
                    'Excepciones': str(e)
                }
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        responses={
            200: 'El usuario ha sido eliminado exitosamente.',
            404: 'El usuario no fue encontrado.',
            500: 'Se ha producido un error en el servidor.'
        }
    ) 
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar un usuario existente

        Para eliminar un usuario, se debe proporcionar el ID único del usuario que se desea eliminar. Debe coincidir con el ID del usuario que se desea eliminar.

        Nota: Este proceso implica cambiar el estado del registro del usuario a "False" para que sea ignorado por los procesos del software. Se mantiene un registro de todos los usuarios que alguna vez ingresaron, por lo que el registro no se elimina de la base de datos.
        """
        try:
            instance = self.get_object()
            if Usuario.objects.filter(id = instance.id, estado = True).exists():
                instance.estado = False
                instance.save()
                return http_200_ok('El usuario se ha eliminado con éxito')
            else:
                return http_400_invalido()
        except Exception as e:
            return Response({
                'estado': 500,
                'validar': False,
                'mensaje': str(e)
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(responses = {404: 'No se encontró la URL solicitada.'}) 
    def list(self, request, *args, **kwargs):
        """
        Obtener todos los registros de usuarios

        Esta función ha sido desactivada debido a su capacidad para filtrar información confidencial del usuario, lo que puede representar un riesgo de seguridad, incluyendo el robo de información personal.
        """
        return http_400_invalido()

    @swagger_auto_schema(responses = {404: 'No se encontró la URL solicitada.'})
    def retrieve(self, request, *args, **kwargs):
        """
        Obtener un registro específico de un usuario

        Esta función ha sido desactivada debido a su capacidad para filtrar información confidencial del usuario, lo que puede representar un riesgo de seguridad, incluyendo el robo de información personal.
        """
        return http_400_invalido()

class LenguajeView(viewsets.ModelViewSet):
    queryset = Lenguaje.objects.filter(estado = True).prefetch_related('nivel_lenguaje')
    serializer_class = LenguajeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses = {404: 'No se encontró la URL solicitada.'})
    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo lenguaje de programación

        Esta información será gestionada exclusivamente por los administradores de manera directa en la base de datos. Por lo tanto, el acceso a esta funcionalidad estará restringido para el resto de los usuarios.
        """
        return http_400_invalido()
    
    @swagger_auto_schema(responses = {404: 'No se encontró la URL solicitada.'})
    def update(self, request, *args, **kwargs):
        """
        Actualizar un lenguaje de programación existente

        Esta información será gestionada exclusivamente por los administradores de manera directa en la base de datos. Por lo tanto, el acceso a esta funcionalidad estará restringido para el resto de los usuarios.
        """
        return http_400_invalido()
    
    @swagger_auto_schema(responses = {404: 'No se encontró la URL solicitada.'})
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar un lenguaje de programación existente

        Esta información será gestionada exclusivamente por los administradores de manera directa en la base de datos. Por lo tanto, el acceso a esta funcionalidad estará restringido para el resto de los usuarios.
        """
        return http_400_invalido()
    
    @swagger_auto_schema(
        responses = {
            200: 'Se ha encontrado y devuelto la información del registro solicitado correctamente.',
            404: 'No se encontró el lenguaje de programación solicitado.',
            500: 'Se ha producido un error en el servidor.'
        }
    ) 
    def retrieve(self, request, pk = None):
        """
        Obtener información detallada de un lenguaje de programación específico

        Esta función devuelve información detallada de un lenguaje de programación específico almacenado en la base de datos, identificado por su ID único. La información incluye los detalles del lenguaje, los niveles que contiene y las preguntas correspondientes a cada nivel.
        """
        try:
            lenguaje = Lenguaje.objects.get(pk = pk, estado = True)
        except Lenguaje.DoesNotExist:
            return Response({
                'estado': 404,
                'validar': False,
                'mensaje': 'Lo sentimos, el lenguaje especificado no está disponible en el sistema'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = self.get_serializer(lenguaje)
            return Response({
                'estado': 200,
                'validar': True,
                'mensaje': 'Lenguaje encontrado! Aquí está la información que solicitaste',
                'datos': serializer.data
            }, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'estado': 500,
                'validar': False,
                'mensaje': str(e)
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)       

class ProgresoView(viewsets.ModelViewSet):
    queryset = Progreso.objects.all()
    serializer_class = ProgresoSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses = {
            201: 'Se ha agregado el progreso al usuario exitosamente.',
            400: 'La solicitud contiene datos incorrectos o incompletos.',
            500: 'Se ha producido un error en el servidor.'
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Agregar un progreso al usuario

        Esta función permite agregar un progreso al usuario, registrando sus actividades y avances en el sistema. Se deben proporcionar los siguientes campos en formato JSON:
        - 'idUsuario': El ID único de un usuario existente.
        - 'idLenguaje': El ID único de un lenguaje de programación existente.
        - 'historial': El historial de actividades realizadas por el usuario. Este campo debe contener los niveles completados por el usuario, dependiendo del progreso alcanzado.
        - 'puntos': Los puntos ganados por el usuario. El usuario acumula puntos a medida que completa preguntas, niveles y lenguajes de programación.
        """
        idUsuario = request.data['idUsuario']
        idLenguaje = request.data['idLenguaje']
        historial = request.data['historial']
        puntos = request.data['puntos']
        mensaje = {}
        datos_validados = True

        if not idUsuario:
            mensaje['usuario'] = 'Por favor, asegúrate de ingresar el usuario. Este campo no puede estar vacío'
            datos_validados = False
        elif not Usuario.objects.filter(id = idUsuario, estado = True).exists():
            mensaje['usuario'] = 'Por favor ingrese otro identificador, el usuario especificado no está disponible en el sistema'
            datos_validados = False
        
        if not idLenguaje:
            mensaje['lenguaje'] = 'Por favor, asegúrate de ingresar el lenguaje. Este campo no puede estar vacío'
            datos_validados = False
        elif not Lenguaje.objects.filter(id = idLenguaje, estado = True).exists():
            mensaje['lenguaje'] = 'Por favor ingrese otro identificador, el lenguaje especificado no está disponible en el sistema'
            datos_validados = False
        
        if Progreso.objects.filter(idUsuario = idUsuario, idLenguaje = idLenguaje).exists():
            mensaje['progreso'] = 'Lo sentimos, ya existe un progreso con los datos proporcionados. Por favor, verifique la información e inténtelo de nuevo'
            datos_validados = False

        if not historial:
            mensaje['historial'] = 'Por favor, asegúrate de ingresar el historial. Este campo no puede estar vacío'
            datos_validados = False
        elif not isinstance(historial, dict):
            mensaje['historial'] = 'Por favor, ingresa un dato válido en formato JSON'
            datos_validados = False
        
        if not puntos:
            mensaje['puntos'] = 'Por favor, asegúrate de ingresar la cantidad de puntos. Este campo no puede estar vacío'
            datos_validados = False

        serializer = self.get_serializer(data = request.data)
        try:
            serializer.is_valid()
            if datos_validados:
                serializer.save()
                return Response({
                    'estado': 201,
                    'validar': True,
                    'mensaje': 'El proceso ha sido agregado exitosamente al usuario'
                }, status = status.HTTP_200_OK)
            else:
                return http_400_error(mensaje)
        except Exception as e:
            return Response({
                'estado': 500,
                'validar': False,
                'mensaje': {
                    'serializador': serializer.errors,
                    'Excepciones': str(e)
                }
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        responses = {
            200: 'El progreso del usuario ha sido actualizado correctamente.',
            400: 'La solicitud contiene datos incorrectos o incompletos.',
            500: 'Se ha producido un error en el servidor.'
        }
    )    
    def update(self, request, *args, **kwargs):
        """
        Actualizar el progreso de un usuario

        Esta función permite actualizar el progreso de un usuario en el sistema. Se deben proporcionar los siguientes campos:
        - 'id': El ID único del progreso existente que se desea actualizar.
        - 'historial': El historial de actividades realizadas por el usuario. Este campo debe contener los niveles completados por el usuario, reflejando el progreso alcanzado.
        - 'puntos': Los puntos ganados por el usuario. El usuario acumula puntos a medida que completa preguntas, niveles y lenguajes de programación.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        historial = request.data['historial']
        puntos = request.data['puntos']
        request.data['idUsuario'] = instance.idUsuario.id
        request.data['idLenguaje'] = instance.idLenguaje.id
        mensaje = {}
        datos_validados = True

        if not historial:
            mensaje['historial'] = 'Por favor, asegúrate de ingresar el historial. Este campo no puede estar vacío'
            datos_validados = False
        elif not isinstance(historial, dict):
            mensaje['historial'] = 'Por favor, ingresa un dato válido en formato JSON'
            datos_validados = False
        
        if not puntos:
            mensaje['puntos'] = 'Por favor, asegúrate de ingresar la cantidad de puntos. Este campo no puede estar vacío'
            datos_validados = False
        
        serializer = self.get_serializer(instance, data = request.data, partial = partial)
        try:
            serializer.is_valid()
            if datos_validados:
                serializer.save()
                return http_200_ok('El proceso del usuario ha sido actualizado exitosamente')
            else:
                return http_400_error(mensaje)
        except Exception as e:
            return Response({
                'estado': 500,
                'validar': False,
                'mensaje': {
                    'serializador': serializer.errors,
                    'Excepciones': str(e)
                }
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(responses = {404: 'No se encontró la URL solicitada.'})
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar el progreso de un usuario existente

        Esta información será gestionada exclusivamente por los administradores de manera directa en la base de datos. Por lo tanto, el acceso a esta funcionalidad estará restringido para el resto de los usuarios.
        """
        return http_400_invalido()
    
    @swagger_auto_schema(
        responses={
            200: 'Se ha obtenido el ranking de usuarios correctamente.',
            500: 'Se ha producido un error en el servidor.'
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Obtener el ranking de usuarios con sus respectivos puntos

        Esta función obtiene el ranking de usuarios en función de la cantidad de puntos que han acumulado. Devuelve una lista de usuarios ordenada por la cantidad de puntos, junto con el nombre de cada usuario y la cantidad de puntos que tiene. Además, se incluye la posición de cada usuario en el ranking.
        """
        try:
            resultados = Progreso.objects.values('idUsuario').annotate(total_puntos=Sum('puntos'))
            lista_usuarios = []
            for indice, resultado in enumerate(sorted(resultados, key=lambda x: x['total_puntos'], reverse=True), start=1):
                id_usuario = resultado['idUsuario']
                usuario = Usuario.objects.get(id = id_usuario)
                nombre = usuario.nombre
                total_puntos = resultado['total_puntos']
                lista_usuarios.append({'puesto': indice, 'nombre': nombre, 'puntos': total_puntos})

            return Response({
                'estado': 200,
                'validar': True,
                'mensaje': 'Ranking de usuarios',
                'datos': lista_usuarios
            }, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'estado': 500,
                'validar': False,
                'mensaje': str(e)
            }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(responses = {404: 'No se encontró la URL solicitada.'})
    def retrieve(self, request, *args, **kwargs):
        """
        Obtener un registro específico de un progreso

        Esta información será gestionada exclusivamente por los administradores de manera directa en la base de datos. Por lo tanto, el acceso a esta funcionalidad estará restringido para el resto de los usuarios.
        """
        return http_400_invalido()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses = {
        200: 'Inicio de sesión exitoso.',
        400: 'La solicitud contiene datos incorrectos o incompletos.',
        500: 'Se ha producido un error en el servidor.'
    }
)
def Log_in(request):
    """
    Iniciar sesión de usuario

    Esta función permite a un usuario iniciar sesión en el sistema. Se deben proporcionar los siguientes campos en formato JSON:
    - 'correo': La dirección de correo electrónico del usuario. No puede estar vacía y debe ser válida.
    - 'password': La contraseña del usuario. No puede estar vacía.
    """
    correo = request.data['correo'].strip()
    password = request.data['password']
    mensaje = {}
    datos_validados = True

    if not correo:
        mensaje['correo'] = 'Por favor, asegúrate de ingresar tu correo electrónico. Este campo no puede estar vacío'
        datos_validados = False
    else:
        try:
            usuario = Usuario.objects.get(correo = correo, estado=True)
        except Usuario.DoesNotExist:
            mensaje['registro'] = 'Lo siento, el correo y/o contraseña ingresados son incorrectos. Por favor, inténtalo nuevamente'
            datos_validados = False

    if not password:
        mensaje['password'] = 'Por favor, asegúrate de ingresar tu contraseña. Este campo no puede estar vacío'
        datos_validados = False
    elif not check_password(password, usuario.password):
        mensaje['registro'] = 'Lo siento, el correo y/o contraseña ingresados son incorrectos. Por favor, inténtalo nuevamente'
        datos_validados = False

    try:
        if datos_validados:
            progreso = Progreso.objects.filter(idUsuario = usuario.id)
            serializerProgreso = ProgresoSerializer(progreso, many = True)
            serializerUsuario = UsuarioSerializer(usuario)
            return Response({
                'estado': 200,
                'validar': True,
                'mensaje': '¡Inicio de sesión exitoso! Aquí está la información que solicitaste',
                'datos': {
                    'usuario': serializerUsuario.data,
                    'progreso': serializerProgreso.data
                }
            }, status = status.HTTP_200_OK)
        else:
            return http_400_error(mensaje)
    except Exception as e:
        return Response({
            'estado': 500,
            'validar': False,
            'mensaje': str(e)
        }, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    responses = {
        200: 'Validación de usuario exitosa.',
        400: 'La solicitud contiene datos incorrectos o incompletos.',
        500: 'Se ha producido un error en el servidor.'
    }
)
def validarUsuario(request):
    """
    Validación de usuario

    Esta función permite validar al usuario utilizando un token temporal asociado a su correo electrónico. Se deben proporcionar los siguientes campos en formato JSON:
    - 'idUsuario': El ID del usuario que se desea validar.
    - 'token': El token temporal generado y enviado al correo del usuario para la validación.
    """
    try:
        limite_de_tiempo = timezone.now() - timedelta(hours = 24)
        try:
            usuarioToken = UsuarioToken.objects.get(token = request.data['token'], idUsuario =  request.data['idUsuario'])
            usuario = Usuario.objects.get(id = usuarioToken.idUsuario.id, estado = False)
        except UsuarioToken.DoesNotExist:
            return Response({
                'estado': 404,
                'validar': False,
                'mensaje': 'Lo sentimos, el token/usuario especificado no está disponible en el sistema'
            }, status = status.HTTP_404_NOT_FOUND)
        
        if usuarioToken.registro < limite_de_tiempo:
            usuarioToken.delete()
            usuario.delete()
            return Response({
                'estado': 404,
                'validar': False,
                'mensaje': 'Lo sentimos, el usuario especificado no está disponible en el sistema debido a que ha superado el tiempo límite'
            }, status = status.HTTP_404_NOT_FOUND)
        else:
            usuario.estado = True
            usuario.save()
            usuarioToken.delete()
            return http_200_ok('Validación de usuario exitosa')
    except Exception as e:
        return Response({
            'estado': 500,
            'validar': False,
            'mensaje': str(e)
        })

def http_200_ok(mensaje):
    return Response({
        'estado': 200,
        'validar': True,
        'mensaje': mensaje
    }, status = status.HTTP_200_OK)

def http_400_invalido():
    return Response({
        'estado': 404,
        'validar': False,
        'mensaje': 'Lo siento, la dirección URL ingresada no es válida. Te sugiero verificarla y volver a intentarlo'
    }, status=status.HTTP_404_NOT_FOUND)

def http_400_error(mensaje):
    return Response({
        'estado': 400,
        'validar': False,
        'mensaje': mensaje
    }, status = status.HTTP_400_BAD_REQUEST)