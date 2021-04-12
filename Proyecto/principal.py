#:vv
from flask import Flask
from flask import request, redirect, url_for, flash,session
from flask import render_template
from flask_mysqldb import MySQL
import datetime
from calculo_precio import calculo_de_importe 

app= Flask(__name__)

#conexión mysql
app.config['MYSQL_HOST'] = 'parkingmx.cykvjrrm8iey.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'luis'
app.config['MYSQL_PASSWORD'] = 'luis12345'
app.config['MYSQL_DB'] = 'parkingmx'
mysql= MySQL(app)

app.secret_key ='mysecretkey'

@app.route('/')
def index (): 
	return render_template ('index.html')

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

	

if __name__ == '__main__':
	app.run(debug = True, port = 8000)