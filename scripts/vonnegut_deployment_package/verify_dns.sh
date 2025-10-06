#!/bin/bash
echo "🔍 Verifying DNS changes for nkllon.com..."
echo

echo "A record for nkllon.com:"
dig nkllon.com A +short

echo
echo "CNAME for www.nkllon.com:"
dig www.nkllon.com CNAME +short

echo
echo "CNAME for observatory.nkllon.com:"
dig observatory.nkllon.com CNAME +short

echo
echo "✅ If you see e567ba2b-df21-47d3-9275-7b8b197f18fc.cfargotunnel.com in the results above,"
echo "   your DNS is configured correctly!"
