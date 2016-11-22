package com.rpatel3001.ru_interested;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class DisplayMessageActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_display_message);

        new DownloadWebpageTask().execute(getIntent().getStringExtra("params"));
    }

    private String downloadUrl(String myurl) throws IOException {
        URL url = new URL(myurl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        Scanner s = new Scanner(conn.getInputStream()).useDelimiter("\\A");
        return s.hasNext() ? s.next() : "";
    }

    private class DownloadWebpageTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... urls) {
            try {
                return downloadUrl(urls[0]);
            } catch (IOException e) {
                return e.getStackTrace().toString();
            }
        }

        @Override
        protected void onPostExecute(String result) {
            try {
                JSONArray rooms = new JSONArray(result);
                ViewGroup layout = (ViewGroup)findViewById(R.id.classlist);

                for(int i = 0; i < rooms.length(); ++i) {
                    ClassDisplayView cl = new ClassDisplayView(getApplicationContext());
                    cl.setValues(new JSONObject(rooms.get(i).toString()));
                    layout.addView(cl);
                }

                findViewById(R.id.loadingPanel).setVisibility(View.GONE);
                layout.setVisibility(View.VISIBLE);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }
}
