FROM docker.elastic.co/elasticsearch/elasticsearch:7.16.3

ENV discovery.type single-node
ENV network.host 0.0.0.0
ENV http.port 9200

EXPOSE 9200

CMD ["/elasticsearch/bin/elasticsearch"]