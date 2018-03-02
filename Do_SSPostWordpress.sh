echo "================="
echo ""
echo "开始更新SS端口..."
python3 /root/SSPostWordpress.py
echo ""
echo "更新完成!"
echo "重启SS..."
/etc/init.d/shadowsocks restart
echo ""

echo "重启firewall..."
firewall-cmd --complete-reload
echo ""
echo ""

echo "更新SS端口完成！"
