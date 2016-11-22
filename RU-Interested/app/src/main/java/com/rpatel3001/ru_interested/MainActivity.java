package com.rpatel3001.ru_interested;

import android.content.Context;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import static android.widget.Toast.LENGTH_SHORT;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void sendMessage(View view) {
        ConnectivityManager connMgr = (ConnectivityManager)
        getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo networkInfo = connMgr.getActiveNetworkInfo();
        if (networkInfo == null || !networkInfo.isConnected()) {
            Toast toast = Toast.makeText(getApplicationContext(), "No Internet connection detected", LENGTH_SHORT);
            toast.show();
            return;
        }
        Intent intent = new Intent(this, DisplayMessageActivity.class);
        String campus = ((Spinner)findViewById(R.id.campus)).getSelectedItem().toString();
        String day = ((Spinner) findViewById(R.id.day)).getSelectedItem().toString();
        int start = Integer.parseInt(((Spinner) findViewById(R.id.starttime)).getSelectedItem().toString());
        int end = Integer.parseInt(((Spinner) findViewById(R.id.endtime)).getSelectedItem().toString());
        String buildings = ((EditText) findViewById(R.id.buildings)).getText().toString();
        String departments = ((EditText) findViewById(R.id.departments)).getText().toString();
        String message = "http://ru-interested.herokuapp.com/api/classes/" + campus + "/" + day + "/" + start + "/" + end + "?buildings=" + buildings + "&departments=" + departments;
        intent.putExtra("params", message);
        startActivity(intent);
    }
}
