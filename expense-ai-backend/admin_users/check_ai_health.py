import os
import requests
from django.core.management.base import BaseCommand
from billing.models import Conversation, ChatMessage
from billing.security import LLMSecurityPipeline

class Command(BaseCommand):
    help = 'Runs a full system diagnostic on the AI Agent and its dependencies.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Lifewood Finance AI Diagnostic ===\n"))

        # 1. Environment Variable Check
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR("[-] OPENAI_API_KEY: MISSING"))
            self.stdout.write("    Check your .env file or environment variables.")
        else:
            self.stdout.write(self.style.SUCCESS(f"[+] OPENAI_API_KEY: FOUND ({api_key[:6]}...)"))

        # 2. Network & API Connectivity Check
        self.stdout.write("\n[*] Testing Connectivity to OpenAI...")
        try:
            # We check the models list as a lightweight way to verify the key and network
            resp = requests.get(
                'https://api.openai.com/v1/models',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )
            if resp.status_code == 200:
                self.stdout.write(self.style.SUCCESS("[+] API Connectivity: OK"))
            else:
                self.stdout.write(self.style.ERROR(f"[-] API Connectivity: FAILED (Status {resp.status_code})"))
                self.stdout.write(f"    Response: {resp.text}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[-] API Connectivity: ERROR ({str(e)})"))

        # 3. LLM Security Pipeline Health
        self.stdout.write("\n[*] Initializing Security Defense Layers...")
        try:
            pipeline = LLMSecurityPipeline()
            test_input = "Hello AI"
            validation = pipeline.protect_input(test_input)
            if not validation.blocked:
                self.stdout.write(self.style.SUCCESS("[+] LLM Security Pipeline: HEALTHY"))
            else:
                self.stdout.write(self.style.WARNING("[!] LLM Security Pipeline: BLOCKED TEST (Check patterns)"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[-] LLM Security Pipeline: FAILED ({str(e)})"))

        # 4. Database Sanity
        conv_count = Conversation.objects.count()
        msg_count = ChatMessage.objects.count()
        self.stdout.write(f"\n[*] Database Status:")
        self.stdout.write(f"    - Conversations: {conv_count}")
        self.stdout.write(f"    - Messages:      {msg_count}")
        
        if conv_count > 0:
            self.stdout.write(self.style.SUCCESS("[+] Database Access: OK"))
        else:
            self.stdout.write(self.style.WARNING("[!] Database Access: OK (but records are empty)"))

        # 5. Configuration Audit
        frontend_url = os.environ.get('FRONTEND_URL')
        self.stdout.write(f"\n[*] Config Audit:")
        self.stdout.write(f"    - FRONTEND_URL: {frontend_url or 'NOT SET (Defaults to https://lifewood.ai)'}")
        
        # Final Verdict
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Diagnostic Complete ===\n"))
        
        if api_key and resp.status_code == 200:
            self.stdout.write(self.style.SUCCESS("Overall Status: AI AGENT IS READY"))
            self.stdout.write("If users still see errors, check individual request timeouts or model availability.")
        else:
            self.stdout.write(self.style.ERROR("Overall Status: SYSTEM ISSUES DETECTED"))
            self.stdout.write("Fix the errors highlighted in RED above to restore service.")