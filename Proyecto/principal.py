from flask import Flask
from flask import request, redirect, url_for, flash,session
from flask import render_template
from flask import url_for,session
from flask_mysqldb import MySQL
import datetime
from calculo_precio import calculo_de_importe 

app= Flask(__name__)

#conexión mysql
app.config['MYSQL_HOST'] = 'parkingmxtestdb.cxr3tycpskvz.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'Albavera'
app.config['MYSQL_PASSWORD'] = 'alba12345'
app.config['MYSQL_DB'] = 'parkingmx'
mysql= MySQL(app)

app.secret_key ='mysecretkey'

@app.route('/')
def index (): 
	return render_template ('index.html')

@app.route('/acceso')
def acceso ():
	return render_template ('acceso.html')

@app.route('/validar_acceso', methods =['POST'])
def validaracceso():
	if request.method == 'POST':

		#obtener datos ingresados en el LOGIN
		usuario = str(request.form['usuario'])
		contraseña = str(request.form['contraseña'])

		#obtener datos de BD Usuarios
		cur = mysql.connection.cursor()
		cur.execute('SELECT * FROM usuarios')
		datos = cur.fetchall()
		
		#validación inicio de sesión
		for dato in datos:
			usuarioBD = str(dato[1])
			contraseñaBD = str(dato[2])
			if usuarioBD == usuario and contraseñaBD == contraseña:# si es exitoso
				flash("Bienvenido {}".format(usuarioBD))
				return redirect(url_for('inicio_usuarios', u = usuario))
		
		#si fracasa
		flash("Usuario o contraseña invalido")
		return redirect(url_for('acceso'))


@app.route('/llegada')
def llegada (): 
	return render_template('llegada.html')

@app.route('/salida')
def salida (): 
	return render_template('salida.html')

@app.route('/registro')
def registro (): 
	return render_template('registro.html')

@app.route('/datosentrada',methods =['POST'])
def datosentrada():
		if request.method == 'POST':
			placas = str(request.form['placas'])
			modelo = request.form['modelo']
			color = request.form['color']
			fecha = request.form['fecha']
			hora = request.form['hora']
			pension = request.form['pension']
			cur = mysql.connection.cursor()
			cur.execute('INSERT INTO entrada(placas,modelo,color,fecha,hora,pension	) VALUES( %s, %s,%s,%s,%s,%s)', (placas,modelo,color,fecha,hora,pension	))
			mysql.connection.commit()
			cur.execute('SELECT * FROM entrada WHERE placas=%s', [placas])
			datos=cur.fetchall()
			
			flash('Te has registrado correctamente y tu ID del boleto es: {}'.format(datos[0][0]))

		
		return redirect(url_for('index'),)
@app.route('/datossalida',methods =['POST'])
def datossalida():
		if request.method == 'POST':
			ident =(request.form['ident'])
			fecha = request.form['fecha']
			hora = request.form['hora']
			cur = mysql.connection.cursor()
			cur.execute('INSERT INTO `parkingmx`.`salida`(id,fecha,hora) VALUES( %s, %s,%s)', (ident,fecha,hora))
			mysql.connection.commit()
			
			#datos entrada mysql
			cur.execute('SELECT * FROM entrada WHERE id=%s', [ident])
			datos= cur.fetchall()
			horae = datos[0][5]
			fechae = datos[0][4]
			pensione = datos[0][6]
			#datos estacionamiento mysql
			cur.execute('SELECT * FROM estacionamiento WHERE id=1' )
			datos2= cur.fetchall()
			tolerancia =datos2[0][5]
			#datos salida mysql
			cur.execute('SELECT * FROM salida WHERE id=%s', [ident])
			datos3= cur.fetchall()
			fechas = datos3[0][1]
			horas = datos3[0][2]

			importe = calculo_de_importe(horae, fechae, horas, fechas, pensione, tolerancia)
			str(importe)
			print("Hora de entrada: ",horae)
			print("Fecha de entrada: ",fechae)
			print("pension",pensione)
			print("tolerancia",tolerancia)

			print("Fecha de salida: ",fechas)
			print("Hora de salida:",horas)
			print("El precio a pagar es de: ${} MXN" .format(importe))
			cur.execute('UPDATE salida SET importe = %s WHERE id = %s', [importe, ident])
			mysql.connection.commit()

			session['var1'] = horae
			session['var2'] = fechae
			session['var3'] = pensione
			session['var4'] = horas
			session['var5'] = fechas
			session['var6'] = (request.form['ident'])
			session['var7'] = pensione
			session['var8'] = importe
			

			


		
		return redirect(url_for('pago'),)

@app.route('/datosestacionamiento',methods =['POST'])
def datosestacionamiento():
		if request.method == 'POST':
			nombre = request.form['nombre']
			cp = request.form['cp']
			telefono = request.form['telefono']
			capacidad = request.form['capacidad']
			tolerancia = request.form['tolerancia']
			cur2 = mysql.connection.cursor()
			cur2.execute('INSERT INTO `parkingmx`.`estacionamiento` (nombre,cp,telefono,capacidad,tolerancia) VALUES( %s,%s,%s,%s,%s)', (nombre,cp,telefono,capacidad,tolerancia))
			mysql.connection.commit()
			flash('Te has registrado correctamente')
			

		
		return redirect(url_for('index'))

@app.route('/pago', methods =['GET','POST'])
def pago (): 

	var1 = session.pop('var1',None)
	var2 = session.pop('var2',None)
	var3 = session.pop('var3',None)
	var4 = session.pop('var4',None)
	var5 = session.pop('var5',None)
	var6 = session.pop('var6',None)
	var7 = session.pop('var7',None)
	var8 = session.pop('var8',None)
	print(var1)
	flash('Pago aceptado')

	return render_template ('pago.html',var1 =var1,var2 =var2,var3 =var3,var4 =var4,var5 =var5,var6 =var6,var7 =var7,var8 =var8)

@app.route('/inicio_usuario/<u>/')
def inicio_usuarios(u = " "):
	return render_template('inicio_usuario.html', u = u)

@app.route('/registro_usuario/<u>/')
def registro_usuario(u = " "):
	cur = mysql.connection.cursor()
	cur.execute('SELECT * FROM usuarios')
	datos = cur.fetchall()
	return render_template('registro_usuario.html', u = u, usuarios = datos)

@app.route('/editar_usuario/<string:id>/<u>/')
def editar_usuario(id,u):
	cur = mysql.connection.cursor()
	cur.execute('SELECT * FROM usuarios WHERE id = {0}'.format(id))
	datos = cur.fetchall()
	return render_template('editar_usuario.html', id = id, u = u ,datos = datos)


@app.route('/borrar_usuario/<string:id>/<u>/')
def borrar_usuario(id,u):
	cur = mysql.connection.cursor()
	cur.execute('DELETE FROM usuarios WHERE id = {0}'.format(id))
	mysql.connection.commit()
	flash('Usuario Eliminado Correctamente')
	return redirect(url_for('registro_usuario', u = u))

@app.route('/actualizar_usuario/<string:id>/<u>/', methods =['POST'])
def actualizar_usuario(id,u):
	if request.method == 'POST':
		usuario = str(request.form['usuario'])
		contraseña = str(request.form['contraseña'])
		cur = mysql.connection.cursor()
		cur.execute('UPDATE usuarios SET usuario = %s, contraseña = %s WHERE id = %s',[usuario, contraseña, id])
		mysql.connection.commit()
		flash('Datos Actualizados Correctamente')
		return redirect(url_for('registro_usuario', u = u))

@app.route('/estacionamientos/<u>/')
def estacionamientos(u):
	cur = mysql.connection.cursor()
	cur.execute('SELECT * FROM estacionamiento')
	datos = cur.fetchall()
	return render_template('estacionamientos.html', u = u, estacionamientos = datos)

@app.route('/borrar_estacionamiento/<string:id>/<u>/')
def borrar_estacionamiento(id,u):
	cur = mysql.connection.cursor()
	cur.execute('DELETE FROM estacionamiento WHERE id = {0}'.format(id))
	mysql.connection.commit()
	flash('Estacionamiento Borrado Correctamente')
	return redirect(url_for('estacionamientos', u = u))

@app.route('/editar_estacionamiento/<string:id>/<u>/')
def editar_estacionamiento(id,u):
	cur = mysql.connection.cursor()
	cur.execute('SELECT * FROM estacionamiento WHERE id = {0}'.format(id))
	datos = cur.fetchall()
	return render_template('editar_estacionamiento.html', id = id, u = u ,datos = datos[0])

@app.route('/actualizar_estacionamiento/<id>/<u>/', methods =['POST'])
def actualizar_estacionamiento(id,u):
	if request.method == 'POST':
		nombre = request.form['nombre']
		cp = request.form['telefono']
		capacidad = request.form['capacidad']
		tolerancia = request.form['tolerancia']
		cur = mysql.connection.cursor()
		cur.execute('UPDATE estacionamiento SET nombre = %s, cp = %s, capacidad = %s, tolerancia = %s WHERE id = %s',[nombre, cp, capacidad, tolerancia, id])
		mysql.connection.commit()
		flash('Datos Actualizados Correctamente')
		return redirect(url_for('estacionamientos', u = u))

@app.route('/autos/<u>/')
def autos(u):
	cur = mysql.connection.cursor()
	cur.execute('SELECT entrada.id, entrada.placas, entrada.modelo, entrada.color, entrada.fecha, entrada.hora, entrada.pension, salida.fecha, salida.hora, salida.importe FROM entrada INNER JOIN salida ON entrada.id=salida.id;')
	datos = cur.fetchall()
	return render_template('autos.html', u = u, datos = datos)

@app.route('/editar_auto/<id>/<u>/')
def editar_auto(id,u):
	cur = mysql.connection.cursor()
	cur.execute('SELECT * FROM entrada WHERE id = %s',[id])
	entrada = cur.fetchall()
	entrada = entrada[0]
	entrada = list(entrada)

	cur = mysql.connection.cursor()
	cur.execute('SELECT * FROM salida WHERE id = %s',[id])
	salida = cur.fetchall()
	salida = salida[0]
	salida = list(salida)

	datos = list()
	datos.extend(entrada)
	datos.extend(salida)
	return render_template('editar_auto.html', id = id, u = u, datos = datos )

@app.route('/actualizar_auto/<id>/<u>/', methods =['POST'])
def actualizar_auto(id,u):
	if request.method == 'POST':
		placas = request.form['placas']
		modelo = request.form['modelo']
		color = request.form['color']
		fecha_entrada = request.form['fecha_entrada']
		hora_entrada = request.form['hora_entrada']
		pension = request.form['pension']

		fecha_salida = request.form['fecha_salida']
		hora_salida = request.form['hora_salida']
		importe = request.form['importe']

		print(fecha_entrada)
		print(fecha_salida)

		cur = mysql.connection.cursor()
		cur.execute('UPDATE entrada SET placas = %s, modelo = %s, color = %s, fecha = %s, hora = %s, pension = %s WHERE id = %s',[placas, modelo, color, fecha_entrada, hora_entrada, pension, id])
		mysql.connection.commit()

		cur = mysql.connection.cursor()
		cur.execute('UPDATE salida SET fecha = %s, hora = %s, importe = %s WHERE id = %s',[fecha_salida, hora_salida, importe,id])
		mysql.connection.commit()
		flash('Datos Actualizados Correctamente')
		return redirect(url_for('autos', u = u))

if __name__ == '__main__':
	app.run(debug = True, port = 8000, host = '0.0.0.0')