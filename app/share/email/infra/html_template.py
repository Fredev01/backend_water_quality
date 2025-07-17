from string import Template
from datetime import datetime


class HtmlTemplate:

    def get_reset_password(self, username, code: int):

        year = datetime.now().year

        template = Template("""
                            <html>
                              <head>
                                <meta charset="UTF-8" />
                                <title>Recuperar contraseña</title>
                              </head>
                              <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                                <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; overflow: hidden;">
                                  <tr>
                                    <td style="background-color: #5accc4; padding: 20px; text-align: center; color: white;">
                                      <h2>Recuperar contraseña</h2>
                                    </td>
                                  </tr>
                                  <tr>
                                    <td style="padding: 30px;">
                                      <p style="font-size: 16px;">Hola <strong> ${username} </strong>,</p>
                                      <p style="font-size: 15px;">
                                        Recibimos una solicitud para restablecer tu contraseña en la plataforma de calidad de agua.
                                      </p>
                                      <p style="font-size: 15px;">
                                        Usa el siguiente código para continuar con el proceso:
                                      </p>
                                      <div style="margin: 20px auto; text-align: center;">
                                        <span style="display: inline-block; background-color: #e9f5f3; color: #004e49; font-size: 24px; padding: 10px 20px; border-radius: 8px; letter-spacing: 4px;">
                                          ${code}
                                        </span>
                                      </div>
                                      <p style="font-size: 14px; color: #555;">Este código es válido por 10 minutos.</p>
                                      <p style="font-size: 14px; color: #555;">Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
                                    </td>
                                  </tr>
                                  <tr>
                                    <td style="background-color: #eeeeee; text-align: center; padding: 15px; font-size: 12px; color: #999;">
                                      © ${year} aqua-minds.org. Todos los derechos reservados.
                                    </td>
                                  </tr>
                                </table>
                              </body>
                            </html>""")
        template = template.substitute(username=username, code=code, year=year)
        return template

    def get_guest_workspace(self, username, owner, id_workspace):
        url_workspace = f'https://aqua-minds.org/#/workspaces/{id_workspace}'

        template = Template("""
                            <html>
                              <head>
                                <meta charset="UTF-8" />
                                <title>Invitación a espacio de trabajo</title>
                              </head>
                              <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                                <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; overflow: hidden;">
                                  <tr>
                                    <td style="background-color: #5accc4; padding: 20px; text-align: center; color: white;">
                                      <h2>Invitación a espacio de trabajo</h2>
                                    </td>
                                  </tr>
                                  <tr>
                                    <td style="padding: 30px;">
                                      <p style="font-size: 16px;">Hola <strong>${username}</strong>,</p>
                                      <p style="font-size: 15px;">
                                        Has sido invitado por <strong>${owner}</strong> a unirte a un espacio de trabajo en la plataforma de calidad de agua.
                                      </p>
                                      <p style="font-size: 15px;">
                                        Puedes acceder al espacio haciendo clic en el siguiente botón:
                                      </p>
                                      <div style="margin: 20px auto; text-align: center;">
                                        <a href="${url}" target="_blank" style="display: inline-block; background-color: #145c57; color: white; font-size: 16px; padding: 12px 24px; border-radius: 6px; text-decoration: none;">
                                          Unirme al espacio
                                        </a>
                                      </div>
                                    </td>
                                  </tr>
                                  <tr>
                                    <td style="background-color: #eeeeee; text-align: center; padding: 15px; font-size: 12px; color: #999;">© ${year} aqua-minds.org. Todos los derechos reservados.
                                    </td>
                                  </tr>
                                </table>
                              </body>
                            </html>""")

        template = template.substitute(
            username=username, owner=owner, url=url_workspace, year=datetime.now().year)

        return template
