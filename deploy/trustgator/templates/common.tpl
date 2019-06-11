{{- define "cloudsql.container" }}
      - name: cloudsql-proxy
        image: gcr.io/cloudsql-docker/gce-proxy:1.11
        command: {{ .Values.cloudsql_command }}
        securityContext: {runAsUser: 2, allowPrivilegeEscalation: false}
        volumeMounts:
        - name: cloudsql-instance-credentials
          mountPath: /secrets/cloudsql
          readOnly: true
{{- end }}

{{- define "cloudsql.volume" }}
      - name: cloudsql-instance-credentials
        secret:
          secretName: {{ .Values.secret_names.sql_creds }}
{{- end }}

{{- define "env.dbvars" }}
        - name: DBHOST
          value: 127.0.0.1
        - name: DBUSER
          value: postgres
        - name: DBPASS
          valueFrom:
            secretKeyRef: {name: {{ .Values.secret_names.sql }}, key: password}
{{- end }}
