import os
import dns.resolver
from pymongo import MongoClient

# cofiguration dns
resolver = dns.resolver.Resolver(
    filename=os.path.join(os.environ["PREFIX"], "etc", "resolv.conf")
)

dns.resolver.default_resolver = resolver

# mongodb connection
uri = "mongodb+srv://edlymulyaandeslin_db_user:3FynoD2yum6s1zDc@cluster0.rcchzhd.mongodb.net/?appName=Cluster0"

client = MongoClient(uri)

db = client["wiki_scraping"]

client.admin.command("ping")

print("MongoDB connected!")
