import plotly.graph_objects as go
import numpy as np
from sympy import lambdify, latex
from pprint import pprint

def plot_2d(X: np.array, variables, var_names, L20, COST, functions, X_min: np.array, Y_min: np.array, latex_formula='', x_inf=20, x_sup=20, y_inf=-3, y_sup=10):
  # print([float(x) for x in X], '\n\n\n')
  # print([float(y) for y in Y], '\n\n\n')
  # print([float(z) for z in Z], '\n\n\n')
  # print(type(X), len(X),type(Y), len(Y),type(Z), len(Z))

  fig = go.Figure()

  # x and y axes
  fig.add_trace(go.Scatter(x=X, y=np.array([0]*len(X)), mode='lines', line=dict(color='black', width=1), opacity=.8, showlegend=False))
  fig.add_trace(go.Scatter(x=np.array([0]*len(X)), y=np.linspace(-50, 50, 10), mode='lines', line=dict(color='black', width=1), opacity=.8, showlegend=False))

  # COST
  fig.add_trace(go.Scatter(x=X, y=np.array([COST(x) for x in X]), mode='lines', name='$COST$'))
  # L20
  fig.add_trace(go.Scatter(x=X, y=np.array([L20([x]) for x in X]), mode='lines', name='$\mathcal{L2O}(\phi)$'))
  # Minima
  fig.add_trace(go.Scatter(x=X_min, y=Y_min, mode='markers', name='Minima'))
  # Original functions
  for i, f in enumerate(functions):
    f_lambda = lambdify(variables, f, 'scipy')
    fig.add_trace(go.Scatter(x=X, y=np.array([f_lambda(x) for x in X]), mode='lines', name=f'$f_{i}={latex(f.subs(var_names))}$', opacity=0.3))


  fig.update_layout(
    title = dict(text=f'${latex_formula}$'),
    scene = dict(
      xaxis = dict(autorange=False, nticks=20, range=[x_inf,x_sup]),
      yaxis = dict(autorange=False, nticks=20, range=[x_sup,y_sup]),

      # zaxis = dict(nticks=4, range=[-100, 100])
    ),
    # width=700,
    # margin=dict(r=20, l=10, b=10, t=10)
  )

  # TODO highlight solutions
  # fig.add_shape(
  #       type="rect",
  #       x0=r[1]["minx"],
  #       x1=r[1]["maxx"],
  #       y0=r[1]["miny"],
  #       y1=r[1]["maxy"],
  #       fillcolor="green",
  #       opacity=0.2,
  #   )

  fig.show()

  # go.Mesh3d(
  #   x=(70*np.random.randn(70)),
  #   y=(55*np.random.randn(70)),
  #   z=(40*np.random.randn(70)),
  #   opacity=0.5,
  #   color='rgba(2,22,100,0.6)'
  # )])
  # """$
  #   \phi := C_1 \land C_2 \land C_3 \land C_4 \qquad\qquad
  #   C_1 \ \equiv \ y<0 \ \lor \ sin(y) = e^x -3 \qquad\qquad
  #   C_3 \ \equiv \ x-y \geq cos(z) \qquad\qquad
  #   C_2 \ \equiv \  y>0 \ \lor \  cos(y) = sin(x^3-z) \qquad\qquad
  #   C_4 \ \equiv \ x+y \leq sin(0.2) \qquad\qquad
  # $"""