import React from 'react';
import ReactDOM from 'react-dom';
import { Tabs } from '@edx/paragon';
import { CourseTeamManagement } from './CourseTeamManagement'

function CourseManagement(props) {
  return (
    <Tabs labels={["Course team management", "Panel 2", "Panel 3"]}>
      <div>
        <CourseTeamManagement orgList={props.teamManagement.list_org}/>
      </div>
      <div>
        Panel 2
      </div>
      <div>
        Panel 3
      </div>
    </Tabs>
  );
}

export class RenderReactComponent {

  constructor(properties={}) {
    Object.assign(this, {
      properties
    });
    this.renderReact();
  }

  renderReact() {
    ReactDOM.render(
      React.createElement(CourseManagement, this.properties, null),
      document.getElementById('root')
    );
  }
}

