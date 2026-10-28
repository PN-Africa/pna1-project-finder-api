import json

from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser
from dj_rest_auth.views import PasswordResetConfirmView
from drf_spectacular.utils import extend_schema

from core.pagination import CustomPageNumberPagination
from .serializers import UserAdminSerializer


UserModel = get_user_model()


# To be removed
class PasswordResetConfirmRedirectView(View):
    """
    Handles the named 'password_reset_confirm' pattern required by dj-rest-auth / Django
    when constructing the password reset link emailed to the user.

    - If requested in a browser (text/html): Renders a reset form to set a new password.
    - If requested via API (application/json): Returns uid and token with endpoint instructions.
    - If POSTed to directly: Injects uid & token from the URL and delegates to PasswordResetConfirmView.
    """

    def get(self, request, uidb64, token, *args, **kwargs):
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'text/html' in accept_header:
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Password - Project Finder</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f172a;
      color: #f8fafc;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
      box-sizing: border-box;
    }}
    .card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 32px;
      width: 100%;
      max-width: 420px;
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
    }}
    h2 {{
      margin: 0 0 8px 0;
      color: #38bdf8;
      font-size: 1.4rem;
    }}
    p {{
      color: #94a3b8;
      font-size: 0.9rem;
      margin-bottom: 24px;
    }}
    label {{
      display: block;
      font-size: 0.85rem;
      color: #94a3b8;
      margin-bottom: 6px;
    }}
    input {{
      width: 100%;
      padding: 10px 12px;
      margin-bottom: 16px;
      border: 1px solid #334155;
      border-radius: 6px;
      background: #0b1120;
      color: #fff;
      box-sizing: border-box;
      font-size: 0.95rem;
    }}
    input:focus {{
      border-color: #38bdf8;
      outline: none;
    }}
    button {{
      width: 100%;
      padding: 12px;
      background: #38bdf8;
      color: #0f172a;
      border: none;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      transition: background 0.2s;
    }}
    button:hover {{
      background: #0ea5e9;
    }}
    button:disabled {{
      opacity: 0.6;
      cursor: not-allowed;
    }}
    #message {{
      margin-top: 16px;
      font-size: 0.88rem;
      padding: 12px;
      border-radius: 6px;
      display: none;
      word-break: break-word;
    }}
    .success {{
      background: rgba(34, 197, 94, 0.15);
      color: #4ade80;
      border: 1px solid #22c55e;
    }}
    .error {{
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid #ef4444;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h2>Reset Password</h2>
    <p>Please enter your new password below.</p>
    <form id="resetForm">
      <label for="new_password1">New Password</label>
      <input type="password" id="new_password1" required minlength="8" />

      <label for="new_password2">Confirm New Password</label>
      <input type="password" id="new_password2" required minlength="8" />

      <button type="submit" id="submitBtn">Set New Password</button>
    </form>
    <div id="message"></div>
  </div>

  <script>
    document.getElementById('resetForm').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const p1 = document.getElementById('new_password1').value;
      const p2 = document.getElementById('new_password2').value;
      const msg = document.getElementById('message');
      const btn = document.getElementById('submitBtn');

      if (p1 !== p2) {{
        msg.className = 'error';
        msg.textContent = 'Passwords do not match.';
        msg.style.display = 'block';
        return;
      }}

      btn.disabled = true;
      btn.textContent = 'Saving...';
      try {{
        const res = await fetch('/api/auth/password/reset/confirm/', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            uid: '{uidb64}',
            token: '{token}',
            new_password1: p1,
            new_password2: p2
          }})
        }});
        const data = await res.json();
        if (res.ok) {{
          msg.className = 'success';
          msg.textContent = data.detail || 'Password successfully reset! You can now log in.';
          msg.style.display = 'block';
          document.getElementById('resetForm').style.display = 'none';
        }} else {{
          msg.className = 'error';
          msg.textContent = Object.values(data).flat().join(' ');
          msg.style.display = 'block';
          btn.disabled = false;
          btn.textContent = 'Set New Password';
        }}
      }} catch (err) {{
        msg.className = 'error';
        msg.textContent = 'Network error: ' + err.message;
        msg.style.display = 'block';
        btn.disabled = false;
        btn.textContent = 'Set New Password';
      }}
    }});
  </script>
</body>
</html>"""
            return HttpResponse(html_content)

        return JsonResponse({
            'detail': 'Password reset confirmation link.',
            'uid': uidb64,
            'token': token,
            'instructions': 'Send a POST request to /api/auth/password/reset/confirm/ with new_password1, new_password2, uid, and token.'
        })

    def post(self, request, uidb64, token, *args, **kwargs):
        # Allows posting directly to /password-reset/confirm/<uidb64>/<token>/
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = {}

        data = {**request.POST.dict(), **body}
        data['uid'] = uidb64
        data['token'] = token

        # Re-encode body as JSON and delegate
        request._body = json.dumps(data).encode('utf-8')
        return PasswordResetConfirmView.as_view()(request, *args, **kwargs)


class UserViewSet(ListModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    
    queryset = UserModel.objects.prefetch_related('simulations').all()
    
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPageNumberPagination

    @extend_schema(
        description="Return a specific user's details"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Returns list of users with their simulation activity"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


